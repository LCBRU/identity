from datetime import datetime
from unittest.mock import call, patch

import pytest

from identity.database import db
from identity.model import Study
from identity.redcap import _load_participants, import_participants
from identity.redcap.model import (EcrfDetail, ParticipantImportDefinition,
                                   RedcapInstance, RedcapProject)
from identity.security import get_system_user
from identity.services.validators import parse_date
from identity.setup.participant_identifier_types import \
    ParticipantIdentifierTypeName

DEFAULT_RECORD = {
    'record': 'abc1',
    'last_update_timestamp': 1,
}


DEFAULT_RESULT = {
    'ecrf_participant_identifier': 'abc1',
    'recruitment_date': None,
    'first_name': None,
    'last_name': None,
    'sex': None,
    'postcode': None,
    'birth_date': None,
    'complete_or_expected': None,
    'withdrawal_date': None,
    'withdrawn_from_study': None,
    'post_withdrawal_keep_samples': None,
    'post_withdrawal_keep_data': None,
    'brc_opt_out': None,
    'excluded_from_analysis': None,
    'excluded_from_study': None,
    'ecrf_timestamp': 1,
}


DEFAULT_IDENTIFIERS = {}

LIST_COLUMNS = [
    ('complete_or_expected', 'complete_or_expected'),
    ('post_withdrawal_keep_samples', 'post_withdrawal_keep_samples'),
    ('post_withdrawal_keep_data', 'post_withdrawal_keep_data'),
    ('brc_opt_out', 'brc_opt_out'),
    ('excluded_from_analysis', 'excluded_from_analysis'),
    ('excluded_from_study', 'excluded_from_study'),
]

DATE_FIELDS = [
    ('recruitment_date', 'recruitment_date'),
    ('birth_date', 'birth_date'),
]

TEXT_FIELDS = [
    ('first_name', 'first_name'),
    ('last_name', 'last_name'),
    ('post_code', 'postcode'),
]


def _get_participant_import_definition(*args, **kwargs):
    r = RedcapInstance.query.first()
    s = Study.query.first()
    p = RedcapProject(name='fred', project_id=1, redcap_instance_id=r.id)

    pid = ParticipantImportDefinition(redcap_project=p, study=s, **kwargs)

    db.session.add(pid)
    db.session.commit()

    return pid


def _run_import_test(participant_import_definition, record, expected, expected_identifiers):
    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [record]

        before = datetime.utcnow()
        
        _load_participants(participant_import_definition, get_system_user())

        db.session.commit()

        after = datetime.utcnow()

        actual = EcrfDetail.query.filter(EcrfDetail.last_updated_datetime.between(before, after)).one_or_none()
        _assert_actual_equals_expected(participant_import_definition, actual, expected, expected_identifiers)


def _assert_actual_equals_expected(participant_import_definition, actual, expected, expected_identifiers):
    assert actual is not None
    assert actual.participant_import_definition_id == participant_import_definition.id
    assert actual.ecrf_participant_identifier == expected['ecrf_participant_identifier']
    assert parse_date(actual.recruitment_date) == expected['recruitment_date']
    assert actual.first_name == expected['first_name']
    assert actual.last_name == expected['last_name']
    assert actual.sex == expected['sex']
    assert actual.postcode == expected['postcode']
    assert parse_date(actual.birth_date) == expected['birth_date']
    assert actual.complete_or_expected == expected['complete_or_expected']
    assert actual.withdrawal_date == expected['withdrawal_date']
    assert actual.withdrawn_from_study == expected['withdrawn_from_study']
    assert actual.post_withdrawal_keep_samples == expected['post_withdrawal_keep_samples']
    assert actual.post_withdrawal_keep_data == expected['post_withdrawal_keep_data']
    assert actual.brc_opt_out == expected['brc_opt_out']
    assert actual.excluded_from_analysis == expected['excluded_from_analysis']
    assert actual.excluded_from_study == expected['excluded_from_study']
    assert actual.ecrf_timestamp == expected['ecrf_timestamp']

    assert len(actual.identifier_source.identifiers) == len(expected_identifiers)

    for i in actual.identifier_source.identifiers:
        assert expected_identifiers[i.participant_identifier_type.name] == i.identifier


def test__import_participants__no_projects(client, faker):
    with patch('identity.redcap._load_participants') as mock__load_participants:

        import_participants()

        mock__load_participants.assert_not_called()


def test__import_participants__one_project(client, faker):
    pid = _get_participant_import_definition()

    with patch('identity.redcap._load_participants') as mock__load_participants:

        import_participants()

        db.session.commit()

        mock__load_participants.assert_called_with(pid, get_system_user())


def test__import_participants__two_project(client, faker):
    pid1 = _get_participant_import_definition()
    pid2 = _get_participant_import_definition()

    with patch('identity.redcap._load_participants') as mock__load_participants:

        import_participants()

        mock__load_participants.assert_has_calls([
            call(pid1, get_system_user()),
            call(pid2, get_system_user()),
        ])


def test__import_participants__all_mappings_null(client, faker):
    pid = _get_participant_import_definition()
    _run_import_test(pid, DEFAULT_RECORD, DEFAULT_RESULT, DEFAULT_IDENTIFIERS)


def test__import_participants__all_mappings_empty(client, faker):
    p = _get_participant_import_definition(
        recruitment_date_column_name='',
        first_name_column_name='',
        last_name_column_name='',
        postcode_column_name='',
        birth_date_column_name='',
        withdrawal_date_column_name='',
        withdrawn_from_study_column_name='',
        sex_column_name='',
        complete_or_expected_column_name='',
        post_withdrawal_keep_samples_column_name='',
        post_withdrawal_keep_data_column_name='',
        brc_opt_out_column_name='',
        excluded_from_analysis_column_name='',
        excluded_from_study_column_name='',
    )
    _run_import_test(p, DEFAULT_RECORD, DEFAULT_RESULT, DEFAULT_IDENTIFIERS)


def test__import_participants__column_names_not_found(client, faker):
    p = _get_participant_import_definition(
        recruitment_date_column_name='bernard',
        first_name_column_name='bernard',
        last_name_column_name='bernard',
        postcode_column_name='bernard',
        birth_date_column_name='bernard',
        withdrawal_date_column_name='bernard',
        withdrawn_from_study_column_name='bernard',
        sex_column_name='bernard',
        complete_or_expected_column_name='bernard',
        post_withdrawal_keep_samples_column_name='bernard',
        post_withdrawal_keep_data_column_name='bernard',
        brc_opt_out_column_name='bernard',
        excluded_from_analysis_column_name='bernard',
        excluded_from_study_column_name='bernard',
    )

    _run_import_test(p, DEFAULT_RECORD, DEFAULT_RESULT, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", DATE_FIELDS)
def test__import_participants__date_field__invalid_date(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{f'{field_name}_column_name': column_name},
    )

    record = {**DEFAULT_RECORD, column_name: 'iuweghfiuweiufg'}

    _run_import_test(p, record, DEFAULT_RESULT, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", DATE_FIELDS)
def test__import_participants__date_field__valid_date(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{f'{field_name}_column_name': column_name},
    )

    record = {**DEFAULT_RECORD, column_name: '01-Jan-2010'}
    result = {**DEFAULT_RESULT, field_name: parse_date('01-Jan-2010')}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", TEXT_FIELDS)
def test__import_participants___text_field__stripped(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{f'{field_name}_column_name': column_name},
    )

    record = {**DEFAULT_RECORD, column_name: '  walter     '}
    result = {**DEFAULT_RESULT, field_name: 'walter'}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


def test__import_participants___sex__not_in_map(client, faker):
    p = _get_participant_import_definition(
        sex_column_name='sex',
        sex_column_map='0:F,1:M',
    )

    record = {**DEFAULT_RECORD, 'sex': '2'}

    _run_import_test(p, record, DEFAULT_RESULT, DEFAULT_IDENTIFIERS)


def test__import_participants___sex__in_map(client, faker):
    p = _get_participant_import_definition(
        sex_column_name='sex',
        sex_column_map='0:F,1:M',
    )

    record = {**DEFAULT_RECORD, 'sex': '0'}
    result = {**DEFAULT_RESULT, 'sex': 'F'}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


def test__import_participants___sex__empty_is_not_zero(client, faker):
    p = _get_participant_import_definition(
        sex_column_name='sex',
        sex_column_map='0:F,1:M',
    )

    record = {**DEFAULT_RECORD, 'sex': ''}

    _run_import_test(p, record, DEFAULT_RESULT, DEFAULT_IDENTIFIERS)


def test__import_participants___sex__empty_map(client, faker):
    p = _get_participant_import_definition(
        sex_column_name='sex',
        sex_column_map='',
    )

    record = {**DEFAULT_RECORD, 'sex': ''}

    _run_import_test(p, record, DEFAULT_RESULT, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__values_is_null(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': None,
        }
    )

    record = {**DEFAULT_RECORD, column_name: 'd'}
    result = {**DEFAULT_RESULT, field_name: None}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__values_is_empty(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': '',
        }
    )

    record = {**DEFAULT_RECORD, column_name: 'd'}
    result = {**DEFAULT_RESULT, field_name: None}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__not_in_array(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c',
        }
    )

    record = {**DEFAULT_RECORD, column_name: 'd'}
    result = {**DEFAULT_RESULT, field_name: False}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__in_array(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c',
        }
    )

    record = {**DEFAULT_RECORD, column_name: 'a'}
    result = {**DEFAULT_RESULT, field_name: True}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__is_null(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c,<isnull>,d',
        }
    )

    record = {**DEFAULT_RECORD, column_name: None}
    result = {**DEFAULT_RESULT, field_name: True}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__is_null_but_isnt(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c,<isnull>,d',
        }
    )

    record = {**DEFAULT_RECORD, column_name: 's'}
    result = {**DEFAULT_RESULT, field_name: False}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__is_not_null(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c,<isnotnull>,d',
        }
    )

    record = {**DEFAULT_RECORD, column_name: ''}
    result = {**DEFAULT_RESULT, field_name: True}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__is_not_null_but_is(client, faker, column_name, field_name):
    p = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c,<isnotnull>,d',
        }
    )

    record = {**DEFAULT_RECORD, column_name: None}
    result = {**DEFAULT_RESULT, field_name: False}

    _run_import_test(p, record, result, DEFAULT_IDENTIFIERS)


def test__import_participants__field_not_in_id_map(client, faker):
    p = _get_participant_import_definition(
        identities_map=''
    )

    IDENTIFIERS = {}

    _run_import_test(p, DEFAULT_RECORD, DEFAULT_RESULT, IDENTIFIERS)


def test__import_participants__field_in_id_map(client, faker):
    p = _get_participant_import_definition(
        identities_map=f'{ParticipantIdentifierTypeName.STUDY_PARTICIPANT_ID}:record'
    )

    IDENTIFIERS = {
        ParticipantIdentifierTypeName.STUDY_PARTICIPANT_ID: 'abc1',
    }

    _run_import_test(p, DEFAULT_RECORD, DEFAULT_RESULT, IDENTIFIERS)
