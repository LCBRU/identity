import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, call
from identity.services.validators import parse_date
from identity.redcap.model import RedcapInstance, EcrfDetail
from identity.redcap import import_participants, _load_participants
from identity.redcap import RedcapProject, BriccsParticipantImportStrategy
from identity.model.id import Study
from identity.security import get_system_user
from identity.database import db


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


@pytest.mark.parametrize(
    "record, expected, identifiers",
    [
        # Normal
        (
            {
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
            },
            {
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
            },
            {
                'study_participant_id': 'abc1',
                'briccs_id': 'abc1',
                'nhs_number': '3333333333',
                'uhl_system_number': 'S1234567',
            }
        ),
        # Missing int_date
        (
            {
                'record': 'abc1',
                'nhs_number': '3333333333',
                's_number': 'S1234567',
                'int_date': '',
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
            },
            {
                'ecrf_participant_identifier': 'abc1',
                'recruitment_date': None,
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
            },
            {
                'study_participant_id': 'abc1',
                'briccs_id': 'abc1',
                'nhs_number': '3333333333',
                'uhl_system_number': 'S1234567',
            }
        ),
        # Missing DOB
        (
            {
                'record': 'abc1',
                'nhs_number': '3333333333',
                's_number': 'S1234567',
                'int_date': '09-jan-2010',
                'first_name': 'Charles',
                'last_name': 'Smith',
                'gender': 'M',
                'address_postcode': 'LE7 9YG',
                'dob': '',
                'study_status_comp_yn': '0',
                'non_complete_rsn': '0',
                'wthdrw_date': '',
                'wthdrwl_optn_chsn': '0',
                'last_update_timestamp': 1
            },
            {
                'ecrf_participant_identifier': 'abc1',
                'recruitment_date': parse_date('09-jan-2010'),
                'first_name': 'Charles',
                'last_name': 'Smith',
                'sex': 'M',
                'postcode': 'LE7 9YG',
                'birth_date': None,
                'complete_or_expected': False,
                'non_completion_reason': '0',
                'withdrawal_date': None,
                'post_withdrawal_keep_samples': True,
                'post_withdrawal_keep_data': True,
                'brc_opt_out': False,
                'ecrf_timestamp': 1,
            },
            {
                'study_participant_id': 'abc1',
                'briccs_id': 'abc1',
                'nhs_number': '3333333333',
                'uhl_system_number': 'S1234567',
            }
        ),
        # With Withdrawal Date
        (
            {
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
                'wthdrw_date': '14-Sep-2020',
                'wthdrwl_optn_chsn': '0',
                'last_update_timestamp': 1
            },
            {
                'ecrf_participant_identifier': 'abc1',
                'recruitment_date': parse_date('09-jan-2010'),
                'first_name': 'Charles',
                'last_name': 'Smith',
                'sex': 'M',
                'postcode': 'LE7 9YG',
                'birth_date': parse_date('02-mar-2000'),
                'complete_or_expected': False,
                'non_completion_reason': '0',
                'withdrawal_date': parse_date('14-Sep-2020'),
                'post_withdrawal_keep_samples': True,
                'post_withdrawal_keep_data': True,
                'brc_opt_out': False,
                'ecrf_timestamp': 1,
            },
            {
                'study_participant_id': 'abc1',
                'briccs_id': 'abc1',
                'nhs_number': '3333333333',
                'uhl_system_number': 'S1234567',
            }
        ),
        # Will Complete
        (
            {
                'record': 'abc1',
                'nhs_number': '3333333333',
                's_number': 'S1234567',
                'int_date': '09-jan-2010',
                'first_name': 'Charles',
                'last_name': 'Smith',
                'gender': 'M',
                'address_postcode': 'LE7 9YG',
                'dob': '02-mar-2000',
                'study_status_comp_yn': '1',
                'non_complete_rsn': '0',
                'wthdrw_date': '14-Sep-2020',
                'wthdrwl_optn_chsn': '0',
                'last_update_timestamp': 1
            },
            {
                'ecrf_participant_identifier': 'abc1',
                'recruitment_date': parse_date('09-jan-2010'),
                'first_name': 'Charles',
                'last_name': 'Smith',
                'sex': 'M',
                'postcode': 'LE7 9YG',
                'birth_date': parse_date('02-mar-2000'),
                'complete_or_expected': True,
                'non_completion_reason': '0',
                'withdrawal_date': parse_date('14-Sep-2020'),
                'post_withdrawal_keep_samples': True,
                'post_withdrawal_keep_data': True,
                'brc_opt_out': False,
                'ecrf_timestamp': 1,
            },
            {
                'study_participant_id': 'abc1',
                'briccs_id': 'abc1',
                'nhs_number': '3333333333',
                'uhl_system_number': 'S1234567',
            }
        ),
        # Sample No Data
        (
            {
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
                'wthdrw_date': '14-Sep-2020',
                'wthdrwl_optn_chsn': '1',
                'last_update_timestamp': 1
            },
            {
                'ecrf_participant_identifier': 'abc1',
                'recruitment_date': parse_date('09-jan-2010'),
                'first_name': 'Charles',
                'last_name': 'Smith',
                'sex': 'M',
                'postcode': 'LE7 9YG',
                'birth_date': parse_date('02-mar-2000'),
                'complete_or_expected': False,
                'non_completion_reason': '0',
                'withdrawal_date': parse_date('14-Sep-2020'),
                'post_withdrawal_keep_samples': True,
                'post_withdrawal_keep_data': False,
                'brc_opt_out': False,
                'ecrf_timestamp': 1,
            },
            {
                'study_participant_id': 'abc1',
                'briccs_id': 'abc1',
                'nhs_number': '3333333333',
                'uhl_system_number': 'S1234567',
            }
        ),
        # Data No Sample
        (
            {
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
                'wthdrw_date': '14-Sep-2020',
                'wthdrwl_optn_chsn': '2',
                'last_update_timestamp': 1
            },
            {
                'ecrf_participant_identifier': 'abc1',
                'recruitment_date': parse_date('09-jan-2010'),
                'first_name': 'Charles',
                'last_name': 'Smith',
                'sex': 'M',
                'postcode': 'LE7 9YG',
                'birth_date': parse_date('02-mar-2000'),
                'complete_or_expected': False,
                'non_completion_reason': '0',
                'withdrawal_date': parse_date('14-Sep-2020'),
                'post_withdrawal_keep_samples': False,
                'post_withdrawal_keep_data': True,
                'brc_opt_out': False,
                'ecrf_timestamp': 1,
            },
            {
                'study_participant_id': 'abc1',
                'briccs_id': 'abc1',
                'nhs_number': '3333333333',
                'uhl_system_number': 'S1234567',
            }
        ),
        # BRC Opt Out
        (
            {
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
                'wthdrw_date': '14-Sep-2020',
                'wthdrwl_optn_chsn': '4',
                'last_update_timestamp': 1
            },
            {
                'ecrf_participant_identifier': 'abc1',
                'recruitment_date': parse_date('09-jan-2010'),
                'first_name': 'Charles',
                'last_name': 'Smith',
                'sex': 'M',
                'postcode': 'LE7 9YG',
                'birth_date': parse_date('02-mar-2000'),
                'complete_or_expected': False,
                'non_completion_reason': '0',
                'withdrawal_date': parse_date('14-Sep-2020'),
                'post_withdrawal_keep_samples': False,
                'post_withdrawal_keep_data': False,
                'brc_opt_out': True,
                'ecrf_timestamp': 1,
            },
            {
                'study_participant_id': 'abc1',
                'briccs_id': 'abc1',
                'nhs_number': '3333333333',
                'uhl_system_number': 'S1234567',
            }
        ),
    ],
)
def test__load_participants__BriccsParticipantImportStrategy__creates_participant(client, faker, record, expected, identifiers):
    p = _get_project('fred', 1)

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [record]

        before = datetime.utcnow()
        
        _load_participants(p, get_system_user())

        db.session.commit()

        after = datetime.utcnow()        

    actual = EcrfDetail.query.filter(EcrfDetail.last_updated_datetime.between(before, after)).one_or_none()
    actual is not None
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

    assert len(actual.identifier_source.identifiers) == len(identifiers)

    for i in actual.identifier_source.identifiers:
        assert identifiers[i.participant_identifier_type.name] == i.identifier


def test__load_participants__BriccsParticipantImportStrategy__updates_participant(client, faker):
    assert False
    p = _get_project('fred', 1)

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [record]

        before = datetime.utcnow()
        
        _load_participants(p, get_system_user())

        db.session.commit()

        after = datetime.utcnow()        

    actual = EcrfDetail.query.filter(EcrfDetail.last_updated_datetime.between(before, after)).one_or_none()
    actual is not None
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

    assert len(actual.identifier_source.identifiers) == len(identifiers)

    for i in actual.identifier_source.identifiers:
        assert identifiers[i.participant_identifier_type.name] == i.identifier


def test__load_participants__BriccsParticipantImportStrategy__deletes_identifier(client, faker):
    assert False
    p = _get_project('fred', 1)

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [record]

        before = datetime.utcnow()
        
        _load_participants(p, get_system_user())

        db.session.commit()

        after = datetime.utcnow()        

    actual = EcrfDetail.query.filter(EcrfDetail.last_updated_datetime.between(before, after)).one_or_none()
    actual is not None
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

    assert len(actual.identifier_source.identifiers) == len(identifiers)

    for i in actual.identifier_source.identifiers:
        assert identifiers[i.participant_identifier_type.name] == i.identifier


def test__load_participants__BriccsParticipantImportStrategy__links_by_identifier(client, faker):
    assert False
    p = _get_project('fred', 1)

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [record]

        before = datetime.utcnow()
        
        _load_participants(p, get_system_user())

        db.session.commit()

        after = datetime.utcnow()        

    actual = EcrfDetail.query.filter(EcrfDetail.last_updated_datetime.between(before, after)).one_or_none()
    actual is not None
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

    assert len(actual.identifier_source.identifiers) == len(identifiers)

    for i in actual.identifier_source.identifiers:
        assert identifiers[i.participant_identifier_type.name] == i.identifier

