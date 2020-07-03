from tests.redcap import _get_project
from unittest.mock import patch, call
from identity.redcap import import_participants
from identity.redcap.model import DreamParticipantImportStrategy
from identity.security import get_system_user


def test__import_participants__no_projects(client, faker):
    with patch('identity.redcap._load_participants') as mock__load_participants:

        import_participants()

        mock__load_participants.assert_not_called()


def test__import_participants__one_project(client, faker):
    p = _get_project('fred', 1, DreamParticipantImportStrategy)

    with patch('identity.redcap._load_participants') as mock__load_participants:

        import_participants()

        mock__load_participants.assert_called_with(p, get_system_user())


def test__import_participants__two_project(client, faker):
    p1 = _get_project('fred', 1, DreamParticipantImportStrategy)
    p2 = _get_project('mary', 2, DreamParticipantImportStrategy)

    with patch('identity.redcap._load_participants') as mock__load_participants:

        import_participants()

        mock__load_participants.assert_has_calls([call(p1, get_system_user()), call(p2, get_system_user())])
