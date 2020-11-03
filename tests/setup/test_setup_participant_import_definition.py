from datetime import datetime
from identity.ecrfs.setup import RedCapEcrfDefinition
from identity.model import Study
from identity.model.sex import SexName
from identity.security import get_system_user
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
import identity
from unittest.mock import patch
import pytest
from identity.database import db
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.model import ParticipantImportDefinition, RedcapInstance, RedcapProject
from identity.setup import create_base_data


EXAMPLE_DEFINITION = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.MARI,
            'projects': [1],
        },
    ],

    'recruitment_date_column_name': 'fred_a',
    'first_name_column_name': 'fred_b',
    'last_name_column_name': 'fred_c',
    'postcode_column_name': 'fred_d',
    'birth_date_column_name': 'fred_e',

    'withdrawal_date_column_name': 'fred_f',
    'withdrawn_from_study_column_name': 'fred_g',
    'withdrawn_from_study_values': ['x', 'y', 'z'],

    'sex_column_name': 'fred_i',
    'sex_column_map': {
        '0': SexName.FEMALE,
        '1': SexName.MALE,
        '9': SexName.NOT_RECORDED
    },

    'complete_or_expected_column_name': 'fred_j',
    'complete_or_expected_values': ['a', 'b', 'c'],

    'post_withdrawal_keep_samples_column_name': 'fred_k',
    'post_withdrawal_keep_samples_values': ['d', 'e', 'f'],

    'post_withdrawal_keep_data_column_name': 'fred_l',
    'post_withdrawal_keep_data_values': ['g', 'h', 'i'],

    'brc_opt_out_column_name': 'fred_m',
    'brc_opt_out_values': ['j', 'k', 'l'],

    'excluded_from_analysis_column_name': 'fred_n',
    'excluded_from_analysis_values': ['m', 'n', 'o'],

    'excluded_from_study_column_name': 'fred_o',
    'excluded_from_study_values': ['p', 'q', 'r'],

    'identity_map': {
        ParticipantIdentifierTypeName.MARI_ID: 'record',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 'uhl_systemn_number',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_number',
    }
}


def test__create_base_data__no_participant_import_definitions(client, faker):
    with patch.object(identity.setup, 'crfs', []):
        create_base_data()

    assert ParticipantImportDefinition.query.count() == 0


def test__create_base_data__an_example_participant_import_definitions(client, faker):
    _test__create_base_data__participant_import_definitions(RedCapEcrfDefinition(EXAMPLE_DEFINITION))


def test__create_base_data__participant_import_definitions__multiple_projects(client, faker):
    definition = RedCapEcrfDefinition(EXAMPLE_DEFINITION)
    definition.crfs = [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.MARI,
            'projects': [1, 2],
        },
    ]

    _test__create_base_data__participant_import_definitions(definition)


def test__create_base_data__participant_import_definitions__multiple_instances(client, faker):
    definition = RedCapEcrfDefinition(EXAMPLE_DEFINITION)
    definition.crfs = [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.MARI,
            'projects': [1, 2],
        },
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.MARI,
            'projects': [4, 5],
        },
    ]

    _test__create_base_data__participant_import_definitions(definition)


def test__create_base_data__participant_import_definitions__multiple_studies(client, faker):
    definition = RedCapEcrfDefinition(EXAMPLE_DEFINITION)
    definition.crfs = [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.MARI,
            'projects': [1, 2],
        },
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.BRICCS,
            'projects': [4, 5],
        },
    ]

    _test__create_base_data__participant_import_definitions(definition)


COLUMN_NAMES = [
    ('recruitment_date_column_name'),
    ('first_name_column_name'),
    ('last_name_column_name'),
    ('postcode_column_name'),
    ('birth_date_column_name'),
    ('withdrawal_date_column_name'),
    ('withdrawn_from_study_column_name'),
    ('sex_column_name'),
    ('complete_or_expected_column_name'),
    ('post_withdrawal_keep_samples_column_name'),
    ('post_withdrawal_keep_data_column_name'),
    ('brc_opt_out_column_name'),
    ('excluded_from_analysis_column_name'),
    ('excluded_from_study_column_name'),
]


LIST_COLUMN_NAMES = [
    ('complete_or_expected_values'),
    ('post_withdrawal_keep_samples_values'),
    ('post_withdrawal_keep_data_values'),
    ('brc_opt_out_values'),
    ('excluded_from_analysis_values'),
    ('excluded_from_study_values'),
]


MAP_COLUMN_NAMES = [
    ('sex_column_map'),
    ('identity_map'),
]

@pytest.mark.parametrize("column_name", COLUMN_NAMES)
def test__create_base_data__participant_import_definitions__empty_column_name(client, faker, column_name):
    definition = RedCapEcrfDefinition(EXAMPLE_DEFINITION)
    setattr(definition, column_name, '')

    _test__create_base_data__participant_import_definitions(definition)


@pytest.mark.parametrize("column_name", [*COLUMN_NAMES, *LIST_COLUMN_NAMES, *MAP_COLUMN_NAMES])
def test__create_base_data__participant_import_definitions__none_column_name(client, faker, column_name):
    definition = RedCapEcrfDefinition(EXAMPLE_DEFINITION)
    setattr(definition, column_name, None)

    _test__create_base_data__participant_import_definitions(definition)


def _test__create_base_data__participant_import_definitions(definition):
    projects = _create_projects(definition.crfs)

    before = datetime.utcnow()
    
    with patch.object(identity.setup, 'crfs', [definition]):
        create_base_data()

    after = datetime.utcnow()

    assert ParticipantImportDefinition.query.count() == len(projects)

    for p in projects:
        actual = ParticipantImportDefinition.query.filter_by(
            study_id=p['study_id'],
            ecrf_source_id=p['redcap_project_id'],
        ).one_or_none()

        assert actual is not None
        assert actual.first_name_column_name == definition.first_name_column_name
        assert actual.last_name_column_name == definition.last_name_column_name
        assert actual.postcode_column_name == definition.postcode_column_name
        assert actual.birth_date_column_name == definition.birth_date_column_name
        assert actual.withdrawal_date_column_name == definition.withdrawal_date_column_name
        assert actual.withdrawn_from_study_column_name == definition.withdrawn_from_study_column_name
        assert actual.withdrawn_from_study_values_list == definition.withdrawn_from_study_values
        assert actual.sex_column_name == definition.sex_column_name
        assert actual.sex_column_map_dictionary == (definition.sex_column_map or {})
        assert actual.complete_or_expected_column_name == definition.complete_or_expected_column_name
        assert actual.complete_or_expected_values_list == (definition.complete_or_expected_values or [])
        assert actual.post_withdrawal_keep_samples_column_name == definition.post_withdrawal_keep_samples_column_name
        assert actual.post_withdrawal_keep_samples_values_list == (definition.post_withdrawal_keep_samples_values or [])
        assert actual.post_withdrawal_keep_data_column_name == definition.post_withdrawal_keep_data_column_name
        assert actual.post_withdrawal_keep_data_values_list == (definition.post_withdrawal_keep_data_values or [])
        assert actual.brc_opt_out_column_name == definition.brc_opt_out_column_name
        assert actual.brc_opt_out_values_list == (definition.brc_opt_out_values or [])
        assert actual.excluded_from_analysis_column_name == definition.excluded_from_analysis_column_name
        assert actual.excluded_from_analysis_values_list == (definition.excluded_from_analysis_values or [])
        assert actual.excluded_from_study_column_name == definition.excluded_from_study_column_name
        assert actual.excluded_from_study_values_list == (definition.excluded_from_study_values or [])
        assert actual.identities_map_dictionary == (definition.identity_map or {})

        assert before < actual.last_updated_datetime < after
        assert actual.last_updated_by_user_id == get_system_user().id


def _create_projects(crfs):
    result = []

    for c in crfs:
        study = Study.query.filter_by(name=c['study']).one_or_none()
        ri = RedcapInstance.query.filter_by(name=c['instance']['name']).one_or_none()

        for project in c['projects']:
            rp = RedcapProject.query.filter_by(redcap_instance_id=ri.id, project_id=project).one_or_none()

            if not rp:
                rp = RedcapProject(
                    redcap_instance_id=ri.id,
                    project_id=project,
                )

                db.session.add(rp)
                db.session.flush()

            result.append(
                {
                    'study_id': study.id,
                    'redcap_project_id': rp.id,
                }
            )

    db.session.commit()
    return result
