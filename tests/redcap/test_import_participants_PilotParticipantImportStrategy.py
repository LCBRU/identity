import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, call
from identity.services.validators import parse_date
from identity.redcap.model import RedcapInstance, EcrfDetail
from identity.redcap import import_participants, _load_participants
from identity.redcap.model import RedcapProject, PilotParticipantImportStrategy
from identity.model.id import Study
from identity.security import get_system_user
from identity.database import db
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
    'ecrf_timestamp': 1,
}

IDENTIFIERS_1 = {
    ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'abc1',
    ParticipantIdentifierType.__PILOT_ID__: 'abc1',
}

def _get_project(name, id):
    r = RedcapInstance.query.first()
    s = Study.query.first()
    pis = PilotParticipantImportStrategy.query.first()
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
    _test_load_participants(record, expected, IDENTIFIERS_1)


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
    _test_load_participants(record, expected, IDENTIFIERS_1)


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
