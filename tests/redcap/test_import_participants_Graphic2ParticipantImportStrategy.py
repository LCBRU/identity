from tests.redcap import _get_project, _test__load_participants__links_by_identifier, _test_load_participants, _test_participant_update
import pytest
from identity.services.validators import parse_date
from identity.redcap.model import Graphic2ParticipantImportStrategy
from identity.model.id import ParticipantIdentifierType


RECORD_1 = {
    'record': 'abc1',
    'date_interview': '09-jan-2010',
    'gender': 'M',
    'dob': '02-mar-2000',
    'exclude_from_analysis': '0',
    'last_update_timestamp': 1
}

RECORD_2 = {
    'record': 'abc2',
    'date_interview': '17-feb-2011',
    'gender': 'F',
    'dob': '11-june-1970',
    'exclude_from_analysis': '1',
    'last_update_timestamp': 2
}

RESULT_1 = {
    'ecrf_participant_identifier': 'abc1',
    'recruitment_date': parse_date('09-jan-2010'),
    'first_name': None,
    'last_name': None,
    'sex': 'M',
    'postcode': None,
    'birth_date': parse_date('02-mar-2000'),
    'complete_or_expected': None,
    'non_completion_reason': None,
    'withdrawal_date': None,
    'withdrawn_from_study': None,
    'post_withdrawal_keep_samples': None,
    'post_withdrawal_keep_data': None,
    'brc_opt_out': None,
    'excluded_from_analysis': False,
    'excluded_from_study': None,
    'ecrf_timestamp': 1,
}

IDENTIFIERS_1 = {
    ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'abc1',
    ParticipantIdentifierType.__GRAPHICS2_ID__: 'abc1',
}

def test__load_participants__create_participant(client, faker):
    _test_load_participants(RECORD_1, RESULT_1, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)


def test__load_participants__excluded_for_analysis__null(client, faker):
    record = RECORD_1.copy()
    record['exclude_from_analysis'] = None
    expected = RESULT_1.copy()
    expected['excluded_from_analysis'] = False
    _test_load_participants(record, expected, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)


def test__load_participants__expected_to_complete(client, faker):
    record = RECORD_1.copy()
    record['exclude_from_analysis'] = '1'
    expected = RESULT_1.copy()
    expected['excluded_from_analysis'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('date_interview', 'recruitment_date'),
        ('gender', 'sex'),
        ('dob', 'birth_date'),
    ]
)
def test__load_participants__null_fields(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = None
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('date_interview', 'recruitment_date'),
        ('dob', 'birth_date'),
    ]
)
def test__load_participants__empty_fields__none(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('gender', 'sex'),
    ]
)
def test__load_participants__empty_fields__empty(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = ''
    _test_load_participants(record, expected, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)


def test__load_participants__updates_participant(client, faker):
    existing = RECORD_2.copy()
    new_data = RECORD_1
    existing['record'] = new_data['record']

    _test_participant_update(existing, new_data, RESULT_1, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)
