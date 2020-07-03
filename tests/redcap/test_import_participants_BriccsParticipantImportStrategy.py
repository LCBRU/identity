from tests.redcap import DEFAULT_RESULT, _get_project, _test__load_participants__links_by_identifier, _test_load_participants, _test_participant_update
import pytest
from identity.services.validators import parse_date
from identity.redcap.model import BriccsParticipantImportStrategy
from identity.model.id import ParticipantIdentifierType


RECORD_1 = {
    'record': 'abc1',
    'nhs_number': '3333333333',
    's_number': 'S1234567',
    'int_date': '09-jan-2010',
    'first_name': 'Charles',
    'last_name': 'Smith',
    'gender': '1',
    'address_postcode': 'LE7 9YG',
    'dob': '02-mar-2000',
    'study_status_comp_yn': '0',
    'non_complete_rsn': '0',
    'wthdrw_date': '',
    'wthdrwl_optn_chsn': '0',
    'last_update_timestamp': 1
}

RECORD_2 = {
    'record': 'abc2',
    'nhs_number': '2222222222',
    's_number': 'S7654321',
    'int_date': '17-feb-2011',
    'first_name': 'Maragaret',
    'last_name': 'Jones',
    'gender': '0',
    'address_postcode': 'LE2 0HY',
    'dob': '11-june-1970',
    'study_status_comp_yn': '1',
    'non_complete_rsn': '1',
    'wthdrw_date': '25-Aug-2013',
    'wthdrwl_optn_chsn': '1',
    'last_update_timestamp': 2
}

RESULT_1 = DEFAULT_RESULT.copy()
RESULT_1.update({
    'ecrf_participant_identifier': 'abc1',
    'recruitment_date': parse_date('09-jan-2010'),
    'first_name': 'Charles',
    'last_name': 'Smith',
    'sex': 'M',
    'postcode': 'LE7 9YG',
    'birth_date': parse_date('02-mar-2000'),
    'complete_or_expected': False,
    'non_completion_reason': '0',
    'withdrawn_from_study': False,
    'post_withdrawal_keep_samples': True,
    'post_withdrawal_keep_data': True,
    'brc_opt_out': False,
    'ecrf_timestamp': 1,
})

IDENTIFIERS_1 = {
    ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'abc1',
    ParticipantIdentifierType.__BRICCS_ID__: 'abc1',
    ParticipantIdentifierType.__NHS_NUMBER__: '3333333333',
    ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 'S1234567',
}

def test__load_participants__create_participant(client, faker):
    _test_load_participants(RECORD_1, RESULT_1, IDENTIFIERS_1, BriccsParticipantImportStrategy)


def test__load_participants__null_status(client, faker):
    record = RECORD_1.copy()
    record['study_status_comp_yn'] = None
    expected = RESULT_1.copy()
    expected['complete_or_expected'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


def test__load_participants__gender_female(client, faker):
    record = RECORD_1.copy()
    record['gender'] = '0'
    expected = RESULT_1.copy()
    expected['sex'] = 'F'
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


def test__load_participants__gender_male(client, faker):
    record = RECORD_1.copy()
    record['gender'] = '1'
    expected = RESULT_1.copy()
    expected['sex'] = 'M'
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


def test__load_participants__expected_to_complete(client, faker):
    record = RECORD_1.copy()
    record['study_status_comp_yn'] = '1'
    expected = RESULT_1.copy()
    expected['complete_or_expected'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


def test__load_participants__with_withdrawal_date(client, faker):
    record = RECORD_1.copy()
    record['wthdrw_date'] = '02-mar-2000'
    expected = RESULT_1.copy()
    expected['withdrawal_date'] = parse_date('02-mar-2000')
    expected['withdrawn_from_study'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


def test__load_participants__sample_no_data(client, faker):
    record = RECORD_1.copy()
    record['wthdrwl_optn_chsn'] = '1'
    expected = RESULT_1.copy()
    expected['post_withdrawal_keep_samples'] = True
    expected['post_withdrawal_keep_data'] = False
    expected['brc_opt_out'] = False
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


def test__load_participants__data_no_sample(client, faker):
    record = RECORD_1.copy()
    record['wthdrwl_optn_chsn'] = '2'
    expected = RESULT_1.copy()
    expected['post_withdrawal_keep_samples'] = False
    expected['post_withdrawal_keep_data'] = True
    expected['brc_opt_out'] = False
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


def test__load_participants__brc_opt_out(client, faker):
    record = RECORD_1.copy()
    record['wthdrwl_optn_chsn'] = '4'
    expected = RESULT_1.copy()
    expected['post_withdrawal_keep_samples'] = False
    expected['post_withdrawal_keep_data'] = False
    expected['brc_opt_out'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('int_date', 'recruitment_date'),
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
        ('gender', 'sex'),
        ('address_postcode', 'postcode'),
        ('dob', 'birth_date'),
        ('non_complete_rsn', 'non_completion_reason'),
        ('wthdrw_date', 'withdrawal_date'),
    ]
)
def test__load_participants__null_fields(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = None
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('int_date', 'recruitment_date'),
        ('dob', 'birth_date'),
        ('wthdrw_date', 'withdrawal_date'),
        ('gender', 'sex'),
    ]
)
def test__load_participants__empty_fields__none(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
        ('address_postcode', 'postcode'),
        ('non_complete_rsn', 'non_completion_reason'),
    ]
)
def test__load_participants__empty_fields__empty(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = ''
    _test_load_participants(record, expected, IDENTIFIERS_1, BriccsParticipantImportStrategy)


def test__load_participants__updates_participant(client, faker):
    existing = RECORD_2.copy()
    new_data = RECORD_1
    existing['record'] = new_data['record']

    _test_participant_update(existing, new_data, RESULT_1, IDENTIFIERS_1, BriccsParticipantImportStrategy)


@pytest.mark.parametrize(
    "field, removed_id",
    [
        ('nhs_number', ParticipantIdentifierType.__NHS_NUMBER__),
        ('s_number', ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__),
    ]

)
def test__load_participants__remove_none_identity(client, faker, field, removed_id):
    existing = RECORD_1.copy()
    new_data = RECORD_1.copy()
    new_data[field] = None
    identifiers = IDENTIFIERS_1.copy()
    del identifiers[removed_id]

    _test_participant_update(existing, new_data, RESULT_1, identifiers, BriccsParticipantImportStrategy)


@pytest.mark.parametrize(
    "field, removed_id",
    [
        ('nhs_number', ParticipantIdentifierType.__NHS_NUMBER__),
        ('s_number', ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__),
    ]

)
def test__load_participants__remove_empty_identity(client, faker, field, removed_id):
    existing = RECORD_1.copy()
    new_data = RECORD_1.copy()
    new_data[field] = ''
    identifiers = IDENTIFIERS_1.copy()
    del identifiers[removed_id]

    _test_participant_update(existing, new_data, RESULT_1, identifiers, BriccsParticipantImportStrategy)


def test__load_participants__links_by_identifier(client, faker):
    _test__load_participants__links_by_identifier(
        participant_a=RECORD_1.copy(),
        participant_b=RECORD_2.copy(),
        identifiers=IDENTIFIERS_1.copy(),
        matching_identifiers=[ParticipantIdentifierType.__NHS_NUMBER__, ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__],
        matching_fields=['nhs_number', 's_number'],
        strategy_class=BriccsParticipantImportStrategy,
    )
