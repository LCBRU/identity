import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, call
from identity.services.validators import parse_date
from identity.redcap.model import RedcapInstance, EcrfDetail
from identity.redcap import import_participants, _load_participants
from identity.redcap.model import RedcapProject, BriccsParticipantImportStrategy
from identity.model.id import Study
from identity.security import get_system_user
from identity.database import db
from identity.model.id import ParticipantIdentifierType


RECORD_1 = {
    'record': 'abc1',
    'nhs_number': '3333333333',
    's_number': 'S1234567',
    'int_date': '09-jan-2010',
    'first_name': 'Charles',
    'last_name': 'Smith',
    'gender': 'M',
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
    'gender': 'F',
    'address_postcode': 'LE2 0HY',
    'dob': '11-june-1970',
    'study_status_comp_yn': '1',
    'non_complete_rsn': '1',
    'wthdrw_date': '25-Aug-2013',
    'wthdrwl_optn_chsn': '1',
    'last_update_timestamp': 2
}

RESULT_1 = {
    'ecrf_participant_identifier': 'abc1',
    'recruitment_date': parse_date('09-jan-2010'),
    'first_name': 'Charles',
    'last_name': 'Smith',
    'sex': 'M',
    'postcode': 'LE7 9YG',
    'birth_date': parse_date('02-mar-2000'),
    'complete_or_expected': False,
    'non_completion_reason': '0',
    'withdrawal_date': None,
    'post_withdrawal_keep_samples': True,
    'post_withdrawal_keep_data': True,
    'brc_opt_out': False,
    'ecrf_timestamp': 1,
}

IDENTIFIERS_1 = {
    ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'abc1',
    ParticipantIdentifierType.__BRICCS_ID__: 'abc1',
    ParticipantIdentifierType.__NHS_NUMBER__: '3333333333',
    ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 'S1234567',
}

def _get_project(name, id):
    r = RedcapInstance.query.first()
    s = Study.query.first()
    pis = BriccsParticipantImportStrategy.query.first()
    p = RedcapProject(name=name, project_id=id, redcap_instance_id=r.id, study_id=s.id,participant_import_strategy_id=pis.id)

    db.session.add(p)
    db.session.commit()

    return p


def test__import_participants__no_projects(client, faker):
    with patch('identity.redcap._load_participants') as mock__load_participants:

        import_participants()

        mock__load_participants.assert_not_called()


def test__import_participants__one_project(client, faker):
    p = _get_project('fred', 1)

    with patch('identity.redcap._load_participants') as mock__load_participants:

        import_participants()

        mock__load_participants.assert_called_with(p, get_system_user())


def test__import_participants__two_project(client, faker):
    p1 = _get_project('fred', 1)
    p2 = _get_project('mary', 2)

    with patch('identity.redcap._load_participants') as mock__load_participants:

        import_participants()

        mock__load_participants.assert_has_calls([call(p1, get_system_user()), call(p2, get_system_user())])


def _test_load_participants(record, expected, expected_identifiers):
    p = _get_project('fred', 1)

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [record]

        before = datetime.utcnow()
        
        _load_participants(p, get_system_user())

        db.session.commit()

        after = datetime.utcnow()        

    actual = EcrfDetail.query.filter(EcrfDetail.last_updated_datetime.between(before, after)).one_or_none()
    _assert_actual_equals_expected(actual, expected, expected_identifiers)


def test__load_participants__create_participant(client, faker):
    _test_load_participants(RECORD_1, RESULT_1, IDENTIFIERS_1)


def test__load_participants__null_status(client, faker):
    record = RECORD_1.copy()
    record['study_status_comp_yn'] = None
    expected = RESULT_1.copy()
    expected['complete_or_expected'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1)


def test__load_participants__expected_to_complete(client, faker):
    record = RECORD_1.copy()
    record['study_status_comp_yn'] = '1'
    expected = RESULT_1.copy()
    expected['complete_or_expected'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1)


def test__load_participants__with_withdrawal_date(client, faker):
    record = RECORD_1.copy()
    record['wthdrw_date'] = '02-mar-2000'
    expected = RESULT_1.copy()
    expected['withdrawal_date'] = parse_date('02-mar-2000')
    _test_load_participants(record, expected, IDENTIFIERS_1)


def test__load_participants__sample_no_data(client, faker):
    record = RECORD_1.copy()
    record['wthdrwl_optn_chsn'] = '1'
    expected = RESULT_1.copy()
    expected['post_withdrawal_keep_samples'] = True
    expected['post_withdrawal_keep_data'] = False
    expected['brc_opt_out'] = False
    _test_load_participants(record, expected, IDENTIFIERS_1)


def test__load_participants__data_no_sample(client, faker):
    record = RECORD_1.copy()
    record['wthdrwl_optn_chsn'] = '2'
    expected = RESULT_1.copy()
    expected['post_withdrawal_keep_samples'] = False
    expected['post_withdrawal_keep_data'] = True
    expected['brc_opt_out'] = False
    _test_load_participants(record, expected, IDENTIFIERS_1)


def test__load_participants__brc_opt_out(client, faker):
    record = RECORD_1.copy()
    record['wthdrwl_optn_chsn'] = '4'
    expected = RESULT_1.copy()
    expected['post_withdrawal_keep_samples'] = False
    expected['post_withdrawal_keep_data'] = False
    expected['brc_opt_out'] = True
    _test_load_participants(record, expected, IDENTIFIERS_1)


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
    _test_load_participants(record, expected, IDENTIFIERS_1)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('int_date', 'recruitment_date'),
        ('dob', 'birth_date'),
        ('wthdrw_date', 'withdrawal_date'),
    ]
)
def test__load_participants__empty_fields__none(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = None
    _test_load_participants(record, expected, IDENTIFIERS_1)


@pytest.mark.parametrize(
    "record_field, expected_field",
    [
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
        ('gender', 'sex'),
        ('address_postcode', 'postcode'),
        ('non_complete_rsn', 'non_completion_reason'),
    ]
)
def test__load_participants__empty_fields__empty(client, faker, record_field, expected_field):
    record = RECORD_1.copy()
    record[record_field] = ''
    expected = RESULT_1.copy()
    expected[expected_field] = ''
    _test_load_participants(record, expected, IDENTIFIERS_1)


def _assert_actual_equals_expected(actual, expected, expected_identifiers):
    assert actual is not None
    assert actual.redcap_project_id == 1
    assert actual.ecrf_participant_identifier == expected['ecrf_participant_identifier']
    assert parse_date(actual.recruitment_date) == expected['recruitment_date']
    assert actual.first_name == expected['first_name']
    assert actual.last_name == expected['last_name']
    assert actual.sex == expected['sex']
    assert actual.postcode == expected['postcode']
    assert parse_date(actual.birth_date) == expected['birth_date']
    assert actual.complete_or_expected == expected['complete_or_expected']
    assert actual.non_completion_reason == expected['non_completion_reason']
    assert actual.withdrawal_date == expected['withdrawal_date']
    assert actual.post_withdrawal_keep_samples == expected['post_withdrawal_keep_samples']
    assert actual.post_withdrawal_keep_data == expected['post_withdrawal_keep_data']
    assert actual.brc_opt_out == expected['brc_opt_out']
    assert actual.ecrf_timestamp == expected['ecrf_timestamp']

    assert len(actual.identifier_source.identifiers) == len(expected_identifiers)

    for i in actual.identifier_source.identifiers:
        assert expected_identifiers[i.participant_identifier_type.name] == i.identifier


def _test_participant_update(existing, new_data, expected, identifiers):
    p = _get_project('fred', 1)

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.side_effect = [[existing], [new_data]]

        # Setup

        _load_participants(p, get_system_user())
        db.session.commit()

        # Do

        before = datetime.utcnow()
        
        _load_participants(p, get_system_user())

        db.session.commit()

        after = datetime.utcnow()        

    assert EcrfDetail.query.count() == 1
    actual = EcrfDetail.query.filter(EcrfDetail.last_updated_datetime.between(before, after)).one_or_none()
    _assert_actual_equals_expected(actual, expected, identifiers)


def test__load_participants__updates_participant(client, faker):
    existing = RECORD_2.copy()
    new_data = RECORD_1
    existing['record'] = new_data['record']

    _test_participant_update(existing, new_data, RESULT_1, IDENTIFIERS_1)


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

    _test_participant_update(existing, new_data, RESULT_1, identifiers)


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

    _test_participant_update(existing, new_data, RESULT_1, identifiers)


def test__load_participants__links_by_identifier(client, faker):
    p = _get_project('fred', 1)

    participant_a = RECORD_1
    participant_b = RECORD_2

    participant_b['nhs_number'] = participant_a['nhs_number']
    participant_b['s_number'] = participant_a['s_number']

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [participant_a, participant_b]

        _load_participants(p, get_system_user())

        db.session.commit()


    a, b = EcrfDetail.query.all()

    assert len(a.identifier_source.identifiers) == 4
    assert len(b.identifier_source.identifiers) == 4

    assert _get_identifier(a, ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__) != _get_identifier(b, ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__)
    assert _get_identifier(a, ParticipantIdentifierType.__BRICCS_ID__) != _get_identifier(b, ParticipantIdentifierType.__BRICCS_ID__)
    assert _get_identifier(a, ParticipantIdentifierType.__NHS_NUMBER__) == _get_identifier(b, ParticipantIdentifierType.__NHS_NUMBER__)
    assert _get_identifier(a, ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__) == _get_identifier(b, ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__)


def _get_identifier(ecrf, name):
    return  [i for i in ecrf.identifier_source.identifiers if i.participant_identifier_type.name == name]
