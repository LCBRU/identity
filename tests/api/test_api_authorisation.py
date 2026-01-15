import pytest
import uuid
from tests.api import add_api_key_to_url
from identity.api.model import ApiKey


paths = [
    ('/api/create_pseudorandom_ids'),
]


@pytest.mark.parametrize("path", paths)
def test__authorisation__no_api_key(client, faker, path):
    resp = client.post(path)

    assert resp.status_code == 401


@pytest.mark.parametrize("path", paths)
def test__authorisation__wrong_api_key(client, faker, path):
    api_key = faker.get_api_key()

    resp = client.post(add_api_key_to_url(ApiKey(key=uuid.uuid4()), path))

    assert resp.status_code == 401


@pytest.mark.parametrize("path", paths)
def test__authorisation__correct_api_key(client, faker, path):
    resp = client.post(add_api_key_to_url(faker.get_api_key(), path))

    assert resp.status_code != 401


@pytest.mark.parametrize("path", paths)
def test__api_call__no_json(client, faker, path):
    resp = client.post(add_api_key_to_url(faker.get_api_key(), path), json={})

    assert resp.status_code == 400
