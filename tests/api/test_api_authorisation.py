import pytest
import uuid
from tests.api import get_api_key, add_parameters_to_url, add_api_key_to_url


paths = [
    ('/api/create_pseudorandom_ids'),
]


@pytest.mark.parametrize("path", paths)
def test__authorisation__no_api_key(client, faker, path):
    resp = client.post(path)

    assert resp.status_code == 401


@pytest.mark.parametrize("path", paths)
def test__authorisation__wrong_api_key(client, faker, path):
    api_key = get_api_key(faker)

    resp = client.post(add_parameters_to_url(path, {'api_key': uuid.uuid4()}))

    assert resp.status_code == 401


@pytest.mark.parametrize("path", paths)
def test__authorisation__correct_api_key(client, faker, path):
    api_key = get_api_key(faker)

    resp = client.post(add_parameters_to_url(path, {'api_key': api_key.key}))

    assert resp.status_code != 401


@pytest.mark.parametrize("path", paths)
def test__api_call__no_json(client, faker, path):
    resp = client.post(add_api_key_to_url(faker, path))

    assert resp.status_code == 400
