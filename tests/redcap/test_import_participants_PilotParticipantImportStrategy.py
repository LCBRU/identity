from tests.redcap import _test_load_participants, _test_participant_update
import pytest
from identity.services.validators import parse_date
from identity.redcap.model import PilotParticipantImportStrategy
from identity.model.id import ParticipantIdentifierType


RECORD_1 = {
    'record': 'abc1',
    'date_time_of_admission': '09-jan-2010',
    'sex': 'M',
    'last_update_timestamp': 1
}

RECORD_2 = {
    'record': 'abc2',
    'date_time_of_admission': '12-mar-2011',
    'sex': 'F',
    'last_update_timestamp': 1
}

RESULT_1 = {
    'ecrf_participant_identifier': 'abc1',
    'recruitment_date': parse_date('09-jan-2010'),
    'first_name': None,
    'last_name': None,
    'sex': 'M',
    'postcode': None,
    'birth_date': None,
    'complete_or_expected': None,
    'non_completion_reason': None,
    'withdrawal_date': None,
    'post_withdrawal_keep_samples': None,
    'post_withdrawal_keep_data': None,
    'brc_opt_out': None,
    'excluded_from_analysis': None,
    'excluded_from_study': None,
    'ecrf_timestamp': 1,
}

IDENTIFIERS_1 = {
    ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'abc1',
    ParticipantIdentifierType.__PILOT_ID__: 'abc1',
}

def test__load_participants__create_participant(client, faker):
    _test_load_participants(RECORD_1, RESULT_1, IDENTIFIERS_1, PilotParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('date_time_of_admission', 'recruitment_date'),
        ('sex', 'sex'),
    ]
)
def test__load_participants__null_fields(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = None
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, PilotParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('date_time_of_admission', 'recruitment_date'),
    ]
)
def test__load_participants__empty_fields__none(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, PilotParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('sex', 'sex'),
    ]
)
def test__load_participants__empty_fields__empty(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = ''
    _test_load_participants(record, expected, IDENTIFIERS_1, PilotParticipantImportStrategy)


def test__load_participants__updates_participant(client, faker):
    existing = RECORD_2.copy()
    new_data = RECORD_1
    existing['record'] = new_data['record']

    _test_participant_update(existing, new_data, RESULT_1, IDENTIFIERS_1, PilotParticipantImportStrategy)
