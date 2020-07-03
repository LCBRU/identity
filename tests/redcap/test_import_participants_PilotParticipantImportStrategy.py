from tests.redcap import DEFAULT_RESULT, _test_load_participants, _test_participant_update
import pytest
from identity.services.validators import parse_date
from identity.redcap.model import PilotParticipantImportStrategy
from identity.model.id import ParticipantIdentifierType


RECORD_1 = {
    'record': 'abc1',
    'date_time_of_admission': '09-jan-2010',
    'sex': '0',
    'last_update_timestamp': 1
}

RECORD_2 = {
    'record': 'abc2',
    'date_time_of_admission': '12-mar-2011',
    'sex': '1',
    'last_update_timestamp': 1
}

RESULT_1 = DEFAULT_RESULT.copy()
RESULT_1.update({
    'ecrf_participant_identifier': 'abc1',
    'recruitment_date': parse_date('09-jan-2010'),
    'sex': 'M',
    'ecrf_timestamp': 1,
})

IDENTIFIERS_1 = {
    ParticipantIdentifierType.__REDCAP_RECORD__: 'abc1',
    ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'abc1',
    ParticipantIdentifierType.__PILOT_ID__: 'abc1',
}

def test__load_participants__create_participant(client, faker):
    _test_load_participants(RECORD_1, RESULT_1, IDENTIFIERS_1, PilotParticipantImportStrategy)


def test__load_participants__sex__female(client, faker):
    record = RECORD_1.copy()
    record['sex'] = '0'
    expected = RESULT_1.copy()
    expected['sex'] = 'M'
    _test_load_participants(record, expected, IDENTIFIERS_1, PilotParticipantImportStrategy)


def test__load_participants__sex__male(client, faker):
    record = RECORD_1.copy()
    record['sex'] = '1'
    expected = RESULT_1.copy()
    expected['sex'] = 'F'
    _test_load_participants(record, expected, IDENTIFIERS_1, PilotParticipantImportStrategy)


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
        ('sex', 'sex'),
    ]
)
def test__load_participants__empty_fields__none(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, PilotParticipantImportStrategy)


def test__load_participants__updates_participant(client, faker):
    existing = RECORD_2.copy()
    new_data = RECORD_1
    existing['record'] = new_data['record']

    _test_participant_update(existing, new_data, RESULT_1, IDENTIFIERS_1, PilotParticipantImportStrategy)
