
from datetime import datetime
from identity.security import get_system_user
from identity.redcap import _load_participants
from unittest.mock import patch
from identity.services.validators import parse_date
from identity.database import db
from identity.model import Study
from identity.redcap.model import EcrfDetail, RedcapInstance, RedcapProject


def _get_project(name, id, strategy_class):
    r = RedcapInstance.query.first()
    s = Study.query.first()
    pis = strategy_class.query.first()
    p = RedcapProject(name=name, project_id=id, redcap_instance_id=r.id, study_id=s.id,participant_import_strategy_id=pis.id)

    db.session.add(p)
    db.session.commit()

    return p


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
    assert actual.withdrawn_from_study == expected['withdrawn_from_study']
    assert actual.post_withdrawal_keep_samples == expected['post_withdrawal_keep_samples']
    assert actual.post_withdrawal_keep_data == expected['post_withdrawal_keep_data']
    assert actual.brc_opt_out == expected['brc_opt_out']
    assert actual.excluded_from_analysis == expected['excluded_from_analysis']
    assert actual.excluded_from_study == expected['excluded_from_study']
    assert actual.ecrf_timestamp == expected['ecrf_timestamp']

    assert len(actual.identifier_source.identifiers) == len(expected_identifiers)

    for i in actual.identifier_source.identifiers:
        assert expected_identifiers[i.participant_identifier_type.name] == i.identifier


def _test_participant_update(existing, new_data, expected, identifiers, strategy_class):
    p = _get_project('fred', 1, strategy_class)

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


def _test_load_participants(record, expected, expected_identifiers, strategy_class):
    p = _get_project('fred', 1, strategy_class)

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [record]

        before = datetime.utcnow()
        
        _load_participants(p, get_system_user())

        db.session.commit()

        after = datetime.utcnow()        

    actual = EcrfDetail.query.filter(EcrfDetail.last_updated_datetime.between(before, after)).one_or_none()
    _assert_actual_equals_expected(actual, expected, expected_identifiers)



def _test__load_participants__links_by_identifier(participant_a, participant_b, identifiers, matching_identifiers, matching_fields, strategy_class):
    for f in matching_fields:
        participant_b[f] = participant_a[f]

    p = _get_project('fred', 1, strategy_class)

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [participant_a, participant_b]

        _load_participants(p, get_system_user())

        db.session.commit()

    a, b = EcrfDetail.query.all()

    assert len(a.identifier_source.identifiers) == len(identifiers)
    assert len(b.identifier_source.identifiers) == len(identifiers)

    for i in identifiers:
        ai = _get_identifier(a, i)
        bi = _get_identifier(b, i)

        if i in matching_identifiers:
            assert ai == bi
        else:
            assert ai != bi


def _get_identifier(ecrf, name):
    return  [i for i in ecrf.identifier_source.identifiers if i.participant_identifier_type.name == name]
