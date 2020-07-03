from tests.redcap import _get_project, _test__load_participants__links_by_identifier, _test_load_participants, _test_participant_update
import pytest
from identity.services.validators import parse_date
from identity.redcap.model import BioresourceLegacyParticipantImportStrategy
from identity.model.id import ParticipantIdentifierType


RECORD_1 = {
    'record': 'abc1',
    'date_of_sig': '09-jan-2010',
    'gender': 'M',
    'date_of_birth': '02-mar-2000',
    'study_status_comp_yn': '0',
    'non_complete_rsn': '0',
    'wthdrw_date': '',
    'wthdrwl_optn_chsn': '0',
    'last_update_timestamp': 1
}

RECORD_2 = {
    'record': 'abc2',
    'date_of_sig': '17-feb-2011',
    'gender': 'F',
    'date_of_birth': '11-june-1970',
    'study_status_comp_yn': '1',
    'non_complete_rsn': '1',
    'wthdrw_date': '25-Aug-2013',
    'wthdrwl_optn_chsn': '1',
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
    'complete_or_expected': False,
    'non_completion_reason': '0',
    'withdrawal_date': None,
    'post_withdrawal_keep_samples': True,
    'post_withdrawal_keep_data': True,
    'brc_opt_out': False,
    'excluded_from_analysis': None,
    'excluded_from_study': None,
    'ecrf_timestamp': 1,
}

IDENTIFIERS_1 = {
    ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'abc1',
    ParticipantIdentifierType.__BIORESOURCE_ID__: 'abc1',
}

def test__load_participants__create_participant(client, faker):
    _test_load_participants(RECORD_1, RESULT_1, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


def test__load_participants__null_status(client, faker):
    record = RECORD_1.copy()
    record['study_status_comp_yn'] = None
    expected = RESULT_1.copy()
    expected['complete_or_expected'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


def test__load_participants__expected_to_complete(client, faker):
    record = RECORD_1.copy()
    record['study_status_comp_yn'] = '1'
    expected = RESULT_1.copy()
    expected['complete_or_expected'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


def test__load_participants__with_withdrawal_date(client, faker):
    record = RECORD_1.copy()
    record['wthdrw_date'] = '02-mar-2000'
    expected = RESULT_1.copy()
    expected['withdrawal_date'] = parse_date('02-mar-2000')
    _test_load_participants(record, expected, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


def test__load_participants__sample_no_data(client, faker):
    record = RECORD_1.copy()
    record['wthdrwl_optn_chsn'] = '1'
    expected = RESULT_1.copy()
    expected['post_withdrawal_keep_samples'] = True
    expected['post_withdrawal_keep_data'] = False
    expected['brc_opt_out'] = False
    _test_load_participants(record, expected, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


def test__load_participants__data_no_sample(client, faker):
    record = RECORD_1.copy()
    record['wthdrwl_optn_chsn'] = '2'
    expected = RESULT_1.copy()
    expected['post_withdrawal_keep_samples'] = False
    expected['post_withdrawal_keep_data'] = True
    expected['brc_opt_out'] = False
    _test_load_participants(record, expected, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


def test__load_participants__brc_opt_out(client, faker):
    record = RECORD_1.copy()
    record['wthdrwl_optn_chsn'] = '4'
    expected = RESULT_1.copy()
    expected['post_withdrawal_keep_samples'] = False
    expected['post_withdrawal_keep_data'] = False
    expected['brc_opt_out'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('date_of_sig', 'recruitment_date'),
        ('gender', 'sex'),
        ('date_of_birth', 'birth_date'),
        ('non_complete_rsn', 'non_completion_reason'),
        ('wthdrw_date', 'withdrawal_date'),
    ]
)
def test__load_participants__null_fields(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = None
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('date_of_sig', 'recruitment_date'),
        ('date_of_birth', 'birth_date'),
        ('wthdrw_date', 'withdrawal_date'),
    ]
)
def test__load_participants__empty_fields__none(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('gender', 'sex'),
        ('non_complete_rsn', 'non_completion_reason'),
    ]
)
def test__load_participants__empty_fields__empty(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = ''
    _test_load_participants(record, expected, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)


def test__load_participants__updates_participant(client, faker):
    existing = RECORD_2.copy()
    new_data = RECORD_1
    existing['record'] = new_data['record']

    _test_participant_update(existing, new_data, RESULT_1, IDENTIFIERS_1, BioresourceLegacyParticipantImportStrategy)
