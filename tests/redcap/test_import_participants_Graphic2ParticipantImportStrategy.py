from tests.redcap import DEFAULT_RESULT, _get_project, _test__load_participants__links_by_identifier, _test_load_participants, _test_participant_update
import pytest
from identity.services.validators import parse_date
from identity.redcap.model import Graphic2ParticipantImportStrategy
from identity.model.id import ParticipantIdentifierType


RECORD_1 = {
    'record': 'abc1',
    'date_interview': '09-jan-2010',
    'gender': '1',
    'dob': '02-mar-2000',
    'exclude_from_analysis': '0',
    'last_update_timestamp': 1
}

RECORD_2 = {
    'record': 'abc2',
    'date_interview': '17-feb-2011',
    'gender': '0',
    'dob': '11-june-1970',
    'exclude_from_analysis': '1',
    'last_update_timestamp': 2
}

RESULT_1 = DEFAULT_RESULT.copy()
RESULT_1.update({
    'ecrf_participant_identifier': 'abc1',
    'recruitment_date': parse_date('09-jan-2010'),
    'sex': 'M',
    'birth_date': parse_date('02-mar-2000'),
    'excluded_from_analysis': False,
    'ecrf_timestamp': 1,
})

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


def test__load_participants__sex__female(client, faker):
    record = RECORD_1.copy()
    record['gender'] = '0'
    expected = RESULT_1.copy()
    expected['sex'] = 'F'
    _test_load_participants(record, expected, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)


def test__load_participants__sex__male(client, faker):
    record = RECORD_1.copy()
    record['gender'] = '1'
    expected = RESULT_1.copy()
    expected['sex'] = 'M'
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
        ('gender', 'sex'),
    ]
)
def test__load_participants__empty_fields__none(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)


def test__load_participants__updates_participant(client, faker):
    existing = RECORD_2.copy()
    new_data = RECORD_1
    existing['record'] = new_data['record']

    _test_participant_update(existing, new_data, RESULT_1, IDENTIFIERS_1, Graphic2ParticipantImportStrategy)
