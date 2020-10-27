from datetime import datetime
from unittest.mock import patch

from identity.database import db
from identity.etl import (ProjectImporter, RedcapProject, import_project_details)
from identity.etl.model import RedcapInstance
from identity.security import get_system_user


def _run_import(records):
    out = ProjectImporter()

    with patch('identity.etl.redcap_engine') as mock__redcap_engine:

        mock__redcap_engine.return_value.__enter__.return_value.execute.side_effect = records

        before = datetime.utcnow()
        
        out.run()

        db.session.commit()

        after = datetime.utcnow()        

    return RedcapProject.query.filter(RedcapProject.last_updated_datetime.between(before, after)).all()


def test__project_importer__no_projects(client, faker):
    actual = _run_import([])
    assert len(actual) == 0


def test__load_instance_projects__creates_project_details(client, faker):
    actual = _run_import([
        [{'project_id': 1, 'app_title': 'Hello'}],
    ])
    assert len(actual) == 1

    assert actual[0].project_id == 1
    assert actual[0].name == 'Hello'


def test__load_instance_projects__multiple_projects(client, faker):
    actual = _run_import([
        [
            {'project_id': 1, 'app_title': 'Hello'},
            {'project_id': 2, 'app_title': 'Goodbye'},
        ],
    ])
    assert len(actual) == 2


def test__load_instance_projects__same_project_different_instances(client, faker):
    actual = _run_import([
        [{'project_id': 1, 'app_title': 'Hello'}],
        [{'project_id': 1, 'app_title': 'Goodbye'}],
    ])
    assert len(actual) == 2


def test__load_instance_projects__updates_existing(client, faker):
    # Setup
    _run_import([
        [{'project_id': 1, 'app_title': 'Hello'}],
    ])

    # Update
    actual = _run_import([
        [{'project_id': 1, 'app_title': 'Goodbye'}],
    ])

    len(actual) == 1
    assert actual[0].project_id == 1
    assert actual[0].name == 'Goodbye'
