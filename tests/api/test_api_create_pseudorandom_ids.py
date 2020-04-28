import pytest
import uuid
from flask import jsonify
from identity.database import db
from identity.printing.discordance import ID_TYPE_PARTICIPANT
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
    resp = client.post(add_api_key_to_url(faker, path), json=dict(
        prefix=ID_TYPE_PARTICIPANT,
        id_count=id_count,
    ))

    assert resp.status_code == 201
    assert resp.json is not None
    assert resp.json['ids'] is not None
    assert len(resp.json['ids']) == id_count
    assert PseudoRandomId.query.filter(PseudoRandomId.full_code.in_(resp.json['ids'])).count() == id_count


def test__create_pseudorandom_ids__no_prefix(client, faker):
    resp = client.post(add_api_key_to_url(faker, path), json=dict(
        id_count=1,
    ))

    assert resp.status_code == 400


def test__create_pseudorandom_ids__no_id_count(client, faker):
    resp = client.post(add_api_key_to_url(faker, path), json=dict(
        prefix=ID_TYPE_PARTICIPANT,
    ))

    assert resp.status_code == 400


def test__create_pseudorandom_ids__prefix_invalid(client, faker):
    resp = client.post(add_api_key_to_url(faker, path), json=dict(
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
    resp = client.post(add_api_key_to_url(faker, path), json=dict(
        prefix=ID_TYPE_PARTICIPANT,
        id_count=id_count,
    ))

    assert resp.status_code == 400
