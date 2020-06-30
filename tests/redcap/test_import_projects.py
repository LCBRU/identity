import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, call
from identity.redcap.model import RedcapInstance
from identity.redcap import import_project_details, _load_instance_projects
from identity.redcap import RedcapProject
from identity.security import get_system_user
from identity.database import db


def test__import_project_details__calls_all_instances(client, faker):
    calls = [call(i) for i in RedcapInstance.query.all()]
    
    with patch('identity.redcap._load_instance_projects') as mock__load_instance_projects:

        import_project_details()

        mock__load_instance_projects.assert_has_calls(calls)


def test__load_instance_projects__creates_project_details(client, faker):
    i = RedcapInstance.query.first()

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [
            {'project_id': 1, 'app_title': 'Hello'},
        ]

        before = datetime.utcnow()
        
        _load_instance_projects(i)
        db.session.commit()

        after = datetime.utcnow()        

    actual = RedcapProject.query.filter(RedcapProject.last_updated_datetime.between(before, after)).one_or_none()
    assert actual is not None
    assert actual.project_id == 1
    assert actual.name == 'Hello'
    assert actual.redcap_instance_id == i.id


def test__load_instance_projects__multiple_projects(client, faker):
    i = RedcapInstance.query.first()

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [
            {'project_id': 1, 'app_title': 'Hello'},
            {'project_id': 2, 'app_title': 'Goodbye'},
        ]

        before = datetime.utcnow()
        
        _load_instance_projects(i)
        db.session.commit()

        after = datetime.utcnow()        

    RedcapProject.query.filter(RedcapProject.last_updated_datetime.between(before, after)).count() == 2


def test__load_instance_projects__updates_existing(client, faker):
    i = RedcapInstance.query.first()

    existing = RedcapProject(
        name='Hello',
        project_id=1,
        redcap_instance=i,
        last_updated_by_user=get_system_user(),
    )

    db.session.add(existing)
    db.session.commit()

    with patch('identity.redcap.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.return_value = [
            {'project_id': 1, 'app_title': 'Goodbye'},
        ]

        before = datetime.utcnow()
        
        _load_instance_projects(i)
        db.session.commit()

        after = datetime.utcnow()        

    actual = RedcapProject.query.filter(RedcapProject.last_updated_datetime.between(before, after)).one_or_none()
    assert actual is not None
    assert actual.project_id == 1
    assert actual.name == 'Goodbye'
    assert actual.redcap_instance_id == i.id
