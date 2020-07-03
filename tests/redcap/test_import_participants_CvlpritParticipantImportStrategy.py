from tests.redcap import DEFAULT_RESULT, _test_load_participants, _test_participant_update
import pytest
from identity.redcap.model import CvlpritParticipantImportStrategy
from identity.model.id import ParticipantIdentifierType


RECORD_1 = {
    'record': 'abc1',
    'patient_id': 'def1',
    'local_id': 'ghi1',
    'sex': '1',
    'last_update_timestamp': 1
}

RECORD_2 = {
    'record': 'abc2',
    'patient_id': 'def2',
    'local_id': 'ghi2',
    'sex': '2',
    'last_update_timestamp': 1
}

RESULT_1 = DEFAULT_RESULT.copy()
RESULT_1.update({
    'ecrf_participant_identifier': 'abc1',
    'sex': 'M',
    'ecrf_timestamp': 1,
})

IDENTIFIERS_1 = {
    ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'def1',
    ParticipantIdentifierType.__CVLPRIT_ID__: 'def1',
    ParticipantIdentifierType.__CVLPRIT_LOCAL_ID__: 'ghi1',
}

def test__load_participants__create_participant(client, faker):
    _test_load_participants(RECORD_1, RESULT_1, IDENTIFIERS_1, CvlpritParticipantImportStrategy)


def test__load_participants__sex__female(client, faker):
    record = RECORD_1.copy()
    record['sex'] = '2'
    expected = RESULT_1.copy()
    expected['sex'] = 'F'
    _test_load_participants(record, expected, IDENTIFIERS_1, CvlpritParticipantImportStrategy)


def test__load_participants__sex__male(client, faker):
    record = RECORD_1.copy()
    record['sex'] = '1'
    expected = RESULT_1.copy()
    expected['sex'] = 'M'
    _test_load_participants(record, expected, IDENTIFIERS_1, CvlpritParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('sex', 'sex'),
    ]
)
def test__load_participants__null_fields(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = None
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, CvlpritParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('sex', 'sex'),
    ]
)
def test__load_participants__empty_fields__none(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, CvlpritParticipantImportStrategy)


def test__load_participants__updates_participant(client, faker):
    existing = RECORD_2.copy()
    new_data = RECORD_1
    existing['record'] = new_data['record']

    _test_participant_update(existing, new_data, RESULT_1, IDENTIFIERS_1, CvlpritParticipantImportStrategy)
