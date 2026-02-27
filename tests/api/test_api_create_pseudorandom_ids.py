import pytest
from identity.model.id import PseudoRandomId
from tests.api import add_api_key_to_url
from lbrc_flask.database import db
from sqlalchemy import select, func


path = '/api/create_pseudorandom_ids'

@pytest.mark.parametrize(
    "id_count",
    [
        (1),
        (10),
    ],
)
def test__create_pseudorandom_ids__valid_json(client, faker, id_count):
    prip = faker.pseudo_random_id_provider().get(save=True)
    resp = client.post(add_api_key_to_url(faker.api_key().get(save=True), path), json=dict(
        prefix=prip.prefix,
        id_count=id_count,
    ))

    assert resp.status_code == 201
    assert resp.json is not None
    assert resp.json['ids'] is not None
    assert len(resp.json['ids']) == id_count
    assert db.session.execute(
        select(func.count(1))
        .where(PseudoRandomId.full_code.in_(resp.json['ids']))
    ).scalar() == id_count


def test__create_pseudorandom_ids__no_prefix(client, faker):
    resp = client.post(add_api_key_to_url(faker.api_key().get(save=True), path), json=dict(
        id_count=1,
    ))

    assert resp.status_code == 400


def test__create_pseudorandom_ids__no_id_count(client, faker):
    prip = faker.pseudo_random_id_provider().get(save=True)
    resp = client.post(add_api_key_to_url(faker.api_key().get(save=True), path), json=dict(
        prefix=prip.prefix,
    ))

    assert resp.status_code == 400


def test__create_pseudorandom_ids__prefix_invalid(client, faker):
    resp = client.post(add_api_key_to_url(faker.api_key().get(save=True), path), json=dict(
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
    prip = faker.pseudo_random_id_provider().get(save=True)
    resp = client.post(
        add_api_key_to_url(faker.api_key().get(save=True), path),
        json=dict(
            prefix=prip.prefix,
            id_count=id_count,
        )
    )

    assert resp.status_code == 400
