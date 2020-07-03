from tests.redcap import DEFAULT_RESULT, _test_load_participants, _test_participant_update
import pytest
from identity.services.validators import parse_date
from identity.redcap.model import DreamParticipantImportStrategy
from identity.model.id import ParticipantIdentifierType


RECORD_1 = {
    'record': 'abc1',
    'date_enrolled': '09-jan-2010',
    'sex': '1',
    'inc_in_eos_analysis': '1',
    'reason_for_participant_rem': None,
    'inc_in_eos_analysis': '1',
    'last_update_timestamp': 1,
}

RECORD_2 = {
    'record': 'abc2',
    'date_enrolled': '12-mar-2011',
    'sex': '2',
    'inc_in_eos_analysis': '0',
    'reason_for_participant_rem': '1',
    'inc_in_eos_analysis': '0',
    'last_update_timestamp': 1,
}

RESULT_1 = DEFAULT_RESULT.copy()
RESULT_1.update({
    'ecrf_participant_identifier': 'abc1',
    'recruitment_date': parse_date('09-jan-2010'),
    'sex': 'M',
    'withdrawn_from_study': False,
    'excluded_from_analysis': False,
    'ecrf_timestamp': 1,
})

IDENTIFIERS_1 = {
    ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'abc1',
    ParticipantIdentifierType.__DREAM_ID__: 'abc1',
}

def test__load_participants__create_participant(client, faker):
    _test_load_participants(RECORD_1, RESULT_1, IDENTIFIERS_1, DreamParticipantImportStrategy)


def test__load_participants__withdrawn_from_study(client, faker):
    record = RECORD_1.copy()
    record['reason_for_participant_rem'] = '6'
    expected = RESULT_1.copy()
    expected['withdrawn_from_study'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, DreamParticipantImportStrategy)


def test__load_participants__excluded_from_analysis__zero(client, faker):
    record = RECORD_1.copy()
    record['inc_in_eos_analysis'] = '0'
    expected = RESULT_1.copy()
    expected['excluded_from_analysis'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, DreamParticipantImportStrategy)


def test__load_participants__sex__male(client, faker):
    record = RECORD_1.copy()
    record['sex'] = '1'
    expected = RESULT_1.copy()
    expected['sex'] = 'M'
    _test_load_participants(record, expected, IDENTIFIERS_1, DreamParticipantImportStrategy)


def test__load_participants__sex__male(client, faker):
    record = RECORD_1.copy()
    record['sex'] = '2'
    expected = RESULT_1.copy()
    expected['sex'] = 'F'
    _test_load_participants(record, expected, IDENTIFIERS_1, DreamParticipantImportStrategy)


def test__load_participants__sex__male(client, faker):
    record = RECORD_1.copy()
    record['sex'] = '3'
    expected = RESULT_1.copy()
    expected['sex'] = 'T'
    _test_load_participants(record, expected, IDENTIFIERS_1, DreamParticipantImportStrategy)


def test__load_participants__sex__male(client, faker):
    record = RECORD_1.copy()
    record['sex'] = '4'
    expected = RESULT_1.copy()
    expected['sex'] = 'O'
    _test_load_participants(record, expected, IDENTIFIERS_1, DreamParticipantImportStrategy)


def test__load_participants__excluded_from_analysis__None(client, faker):
    record = RECORD_1.copy()
    record['inc_in_eos_analysis'] = None
    expected = RESULT_1.copy()
    expected['excluded_from_analysis'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, DreamParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('date_enrolled', 'recruitment_date'),
        ('sex', 'sex'),
    ]
)
def test__load_participants__null_fields(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = None
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, DreamParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('date_enrolled', 'recruitment_date'),
        ('sex', 'sex'),
    ]
)
def test__load_participants__empty_fields__none(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, DreamParticipantImportStrategy)


def test__load_participants__updates_participant(client, faker):
    existing = RECORD_2.copy()
    new_data = RECORD_1
    existing['record'] = new_data['record']

    _test_participant_update(existing, new_data, RESULT_1, IDENTIFIERS_1, DreamParticipantImportStrategy)
