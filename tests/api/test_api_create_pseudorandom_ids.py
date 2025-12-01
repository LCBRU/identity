import pytest
from identity.model.id import PseudoRandomId
from tests.api import add_api_key_to_url


path = '/api/create_pseudorandom_ids'

@pytest.mark.parametrize(
    "id_count",
    [
        (1),
        (10),
    ],
)
def test__create_pseudorandom_ids__valid_json(client, faker, id_count):
    prip = faker.get_test_pseudo_random_id_provider()
    resp = client.post(add_api_key_to_url(faker.get_api_key(), path), json=dict(
        prefix=prip.prefix,
        id_count=id_count,
    ))

    assert resp.status_code == 201
    assert resp.json is not None
    assert resp.json['ids'] is not None
    assert len(resp.json['ids']) == id_count
    assert PseudoRandomId.query.filter(PseudoRandomId.full_code.in_(resp.json['ids'])).count() == id_count


def test__create_pseudorandom_ids__no_prefix(client, faker):
    resp = client.post(add_api_key_to_url(faker.get_api_key(), path), json=dict(
        id_count=1,
    ))

    assert resp.status_code == 400


def test__create_pseudorandom_ids__no_id_count(client, faker):
    prip = faker.get_test_pseudo_random_id_provider()
    resp = client.post(add_api_key_to_url(faker.get_api_key(), path), json=dict(
        prefix=prip.prefix,
    ))

    assert resp.status_code == 400


def test__create_pseudorandom_ids__prefix_invalid(client, faker):
    resp = client.post(add_api_key_to_url(faker.get_api_key(), path), json=dict(
        prefix='NONENEHIUEIUEIUG',
        id_count=1,
    ))

    assert resp.status_code == 400


@pytest.mark.parametrize(
    "id_count",
    [
        (0),
        (-1),
    ],
)
def test__create_pseudorandom_ids__invalid_id_count(client, faker, id_count):
    prip = faker.get_test_pseudo_random_id_provider()
    resp = client.post(
        add_api_key_to_url(faker.get_api_key(), path),
        json=dict(
            prefix=prip.prefix,
            id_count=id_count,
        )
    )

    assert resp.status_code == 400
