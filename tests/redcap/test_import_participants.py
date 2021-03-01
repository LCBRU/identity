from datetime import datetime
from unittest.mock import patch
from copy import deepcopy

import pytest

from lbrc_flask.database import db
from identity.model import Study
from identity.ecrfs import import_participants
from identity.ecrfs.model import (
    EcrfDetail,
    ParticipantImportDefinition,
    RedcapInstance,
    RedcapProject,
)
from lbrc_flask.validators import parse_date
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName

DEFAULT_RECORD = {
    'record': 'abc1',
    'last_update_timestamp': 1,
}


DEFAULT_RESULT = {
    'ecrf': {
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
    },
    'identifiers': {}
}


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


def _define_result(pid, fields=None, identifiers=None, id=None):
    fields = fields or {}
    identifiers = identifiers or {}
    id = id or 'abc1'

    result = {id: deepcopy(DEFAULT_RESULT)}

    for f, v in fields.items():
       result[id]['ecrf'][f] = v

    result[id]['ecrf']['ecrf_participant_identifier'] = id
    result[id]['identifiers'] = identifiers

    return {pid.id: result}


def _get_participant_import_definition(*args, **kwargs):
    r = RedcapInstance.query.first()
    s = Study.query.first()
    p = RedcapProject(name='fred', project_id=1, redcap_instance_id=r.id)

    pid = ParticipantImportDefinition(ecrf_source=p, study=s, **kwargs)

    db.session.add(pid)
    db.session.commit()

    return pid


def _run_import_test(record, expected, new_timestamps=None):
    with patch('identity.ecrfs.model.redcap_engine') as mock__redcap_engine, patch('identity.ecrfs.model.RedcapInstance.get_newest_timestamps') as mock__get_newest_timestamps:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [record]
        mock__get_newest_timestamps.return_value = new_timestamps or {1: 10}

        before = datetime.utcnow()
        
        import_participants()

        db.session.commit()

        after = datetime.utcnow()

        actuals = EcrfDetail.query.filter(EcrfDetail.last_updated_datetime.between(before, after)).all()

        assert len(actuals) == len(expected)

        for a in actuals:
            _assert_actual_equals_expected(a, expected)


def _assert_actual_equals_expected(actual, expected):
    assert actual.participant_import_definition_id in expected
    assert actual.ecrf_participant_identifier in expected[actual.participant_import_definition_id]

    e_ecrf = expected[actual.participant_import_definition_id][actual.ecrf_participant_identifier]['ecrf']
    e_ids = expected[actual.participant_import_definition_id][actual.ecrf_participant_identifier]['identifiers']
    
    assert actual is not None
    assert actual.ecrf_participant_identifier == e_ecrf['ecrf_participant_identifier']
    assert parse_date(actual.recruitment_date) == e_ecrf['recruitment_date']
    assert actual.first_name == e_ecrf['first_name']
    assert actual.last_name == e_ecrf['last_name']
    assert actual.sex == e_ecrf['sex']
    assert actual.postcode == e_ecrf['postcode']
    assert parse_date(actual.birth_date) == e_ecrf['birth_date']
    assert actual.complete_or_expected == e_ecrf['complete_or_expected']
    assert actual.withdrawal_date == e_ecrf['withdrawal_date']
    assert actual.withdrawn_from_study == e_ecrf['withdrawn_from_study']
    assert actual.post_withdrawal_keep_samples == e_ecrf['post_withdrawal_keep_samples']
    assert actual.post_withdrawal_keep_data == e_ecrf['post_withdrawal_keep_data']
    assert actual.brc_opt_out == e_ecrf['brc_opt_out']
    assert actual.excluded_from_analysis == e_ecrf['excluded_from_analysis']
    assert actual.excluded_from_study == e_ecrf['excluded_from_study']
    assert actual.ecrf_timestamp == e_ecrf['ecrf_timestamp']

    assert len(actual.identifier_source.identifiers) == len(e_ids)

    for i in actual.identifier_source.identifiers:
        assert e_ids[i.participant_identifier_type.name] == i.identifier


def test__import_participants__all_mappings_null(client, faker):
    pid = _get_participant_import_definition()
    _run_import_test(
        record=DEFAULT_RECORD,
        expected=_define_result(pid),
    )


def test__import_participants__no_projects(client, faker):
    _run_import_test(
        record=DEFAULT_RECORD,
        expected={},
    )


def test__import_participants__one_project(client, faker):
    pid = _get_participant_import_definition()
    _run_import_test(
        record=DEFAULT_RECORD,
        expected=_define_result(pid),
    )


def test__import_participants__two_project(client, faker):
    pid1 = _get_participant_import_definition()
    pid2 = _get_participant_import_definition()

    expected1=_define_result(pid1)
    expected2=_define_result(pid2)
    expected = {**expected1, **expected2}

    _run_import_test(
        record=DEFAULT_RECORD,
        expected=expected,
    )


def test__import_participants__all_mappings_null(client, faker):
    pid = _get_participant_import_definition()
    _run_import_test(
        record=DEFAULT_RECORD,
        expected=_define_result(pid),
    )


def test__import_participants__all_mappings_empty(client, faker):
    pid = _get_participant_import_definition(
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
    _run_import_test(
        record=DEFAULT_RECORD,
        expected=_define_result(pid),
    )


def test__import_participants__column_names_not_found(client, faker):
    pid = _get_participant_import_definition(
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

    _run_import_test(
        record=DEFAULT_RECORD,
        expected=_define_result(pid),
    )


@pytest.mark.parametrize("column_name, field_name", DATE_FIELDS)
def test__import_participants__date_field__invalid_date(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{f'{field_name}_column_name': column_name},
    )

    record = {**DEFAULT_RECORD, column_name: 'iuweghfiuweiufg'}

    _run_import_test(
        record=record,
        expected=_define_result(pid),
    )


@pytest.mark.parametrize("column_name, field_name", DATE_FIELDS)
def test__import_participants__date_field__valid_date(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{f'{field_name}_column_name': column_name},
    )

    record = {**DEFAULT_RECORD, column_name: '01-Jan-2010'}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: parse_date('01-Jan-2010')}),
    )


@pytest.mark.parametrize("column_name, field_name", TEXT_FIELDS)
def test__import_participants___text_field__stripped(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{f'{field_name}_column_name': column_name},
    )

    record = {**DEFAULT_RECORD, column_name: '  walter     '}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: 'walter'}),
    )


def test__import_participants___sex__not_in_map(client, faker):
    pid = _get_participant_import_definition(
        sex_column_name='sex',
        sex_column_map='0:F,1:M',
    )

    record = {**DEFAULT_RECORD, 'sex': '2'}

    _run_import_test(
        record=record,
        expected=_define_result(pid),
    )


def test__import_participants___sex__in_map(client, faker):
    pid = _get_participant_import_definition(
        sex_column_name='sex',
        sex_column_map='0:F,1:M',
    )

    record = {**DEFAULT_RECORD, 'sex': '0'}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={'sex': 'F'}),
    )


def test__import_participants___sex__empty_is_not_zero(client, faker):
    pid = _get_participant_import_definition(
        sex_column_name='sex',
        sex_column_map='0:F,1:M',
    )

    record = {**DEFAULT_RECORD, 'sex': ''}

    _run_import_test(
        record=record,
        expected=_define_result(pid),
    )


def test__import_participants___sex__empty_map(client, faker):
    pid = _get_participant_import_definition(
        sex_column_name='sex',
        sex_column_map='',
    )

    record = {**DEFAULT_RECORD, 'sex': ''}

    _run_import_test(
        record=record,
        expected=_define_result(pid),
    )


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__values_is_null(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': None,
        }
    )

    record = {**DEFAULT_RECORD, column_name: 'd'}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: None}),
    )


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__values_is_empty(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': '',
        }
    )

    record = {**DEFAULT_RECORD, column_name: 'd'}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: None}),
    )


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__not_in_array(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c',
        }
    )

    record = {**DEFAULT_RECORD, column_name: 'd'}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: False}),
    )


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__in_array(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c',
        }
    )

    record = {**DEFAULT_RECORD, column_name: 'a'}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: True}),
    )


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__is_null(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c,<isnull>,d',
        }
    )

    record = {**DEFAULT_RECORD, column_name: None}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: True}),
    )


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__is_null_but_isnt(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c,<isnull>,d',
        }
    )

    record = {**DEFAULT_RECORD, column_name: 's'}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: False}),
    )


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__is_not_null(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c,<isnotnull>,d',
        }
    )

    record = {**DEFAULT_RECORD, column_name: ''}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: True}),
    )


@pytest.mark.parametrize("column_name, field_name", LIST_COLUMNS)
def test__import_participants__list_column__is_not_null_but_is(client, faker, column_name, field_name):
    pid = _get_participant_import_definition(
        **{
            f'{field_name}_column_name': column_name,
            f'{field_name}_values': 'a,b,c,<isnotnull>,d',
        }
    )

    record = {**DEFAULT_RECORD, column_name: None}

    _run_import_test(
        record=record,
        expected=_define_result(pid, fields={field_name: False}),
    )


def test__import_participants__field_not_in_id_map(client, faker):
    pid = _get_participant_import_definition(
        identities_map=''
    )

    _run_import_test(
        record=DEFAULT_RECORD,
        expected=_define_result(pid),
    )


def test__import_participants__field_in_id_map(client, faker):
    pid = _get_participant_import_definition(
        identities_map=f'{ParticipantIdentifierTypeName.STUDY_PARTICIPANT_ID}:record'
    )

    _run_import_test(
        record=DEFAULT_RECORD,
        expected=_define_result(pid, identifiers={ParticipantIdentifierTypeName.STUDY_PARTICIPANT_ID: 'abc1'}),
    )


def test__import_participants__no_previous_timestamp__loads(client, faker):
    pid = _get_participant_import_definition()

    _run_import_test(
        record=DEFAULT_RECORD,
        expected=_define_result(pid),
    )


def test__import_participants__previous_timestamp_lower__loads(client, faker):
    pid = _get_participant_import_definition()

    # Setup
    _run_import_test(
        record=DEFAULT_RECORD,
        expected=_define_result(pid),
    )

    # Test
    _run_import_test(
        record={**DEFAULT_RECORD, 'record': 'xyz', 'last_update_timestamp': 100},
        expected=_define_result(pid, fields={'ecrf_timestamp': 100}, id='xyz'),
    )


def test__import_participants__previous_timestamp_higher__no_load(client, faker):
    pid = _get_participant_import_definition()

    # Setup
    _run_import_test(
        record={**DEFAULT_RECORD, 'last_update_timestamp': 100},
        expected=_define_result(pid, fields={'ecrf_timestamp': 100}),
    )

    # Test
    _run_import_test(
        record={**DEFAULT_RECORD, 'record': 'xyz', 'last_update_timestamp': 10},
        expected=[],
    )


def test__import_participants__no_new_timestamp__no_load(client, faker):
    pid = _get_participant_import_definition()

    # Setup
    _run_import_test(
        record={**DEFAULT_RECORD, 'last_update_timestamp': 100},
        expected=[],
        new_timestamps={2: 0},
    )

