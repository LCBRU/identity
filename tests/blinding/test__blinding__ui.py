import pytest
from lbrc_flask.pytest.asserts import assert__requires_login
from flask import url_for
from lbrc_flask.pytest.helpers import login
from identity.blinding.model import (
    Blinding,
)
from lbrc_flask.database import db


def _url(study_id, external=True):
    return url_for('ui.blinding', id=study_id, _external=external)


def _blinding_post(client, blinding_set, unblind_id):
    return client.post(
        _url(study_id=blinding_set.study.id, external=False),
        data={
            'id': unblind_id,
            'blinding_set_id': blinding_set.id,
        },
        follow_redirects=True,
    )


def _assert__blinding(blinding_set, resp):
    for bt in blinding_set.blinding_types:
        assert (
            Blinding.query
            .filter_by(blinding_type_id=bt.id)
            .filter_by(unblind_id='hello')
            .count()
        ) == 1
        b = (
            Blinding.query
            .filter_by(blinding_type_id=bt.id)
            .filter_by(unblind_id='hello')
            .first()
        )
        assert b is not None
        dt = resp.soup.find("dt", string=bt.name)
        assert dt is not None
        dd = dt.find_next_sibling("dd")
        assert dd.string == b.pseudo_random_id.full_code



def test_url_requires_login_get(client, faker):
    s = faker.get_test_study()
    assert__requires_login(client, _url(study_id=s.id, external=False), post=True)


@pytest.mark.parametrize(
    "count", [1, 2, 10],
)
def test__ui_blinding__blinding(client, faker, count):
    user = login(client, faker)

    s = faker.get_test_study(owner=user)
    bs = faker.get_test_blinding_set(study=s)

    for _ in range(count):
        faker.get_test_blinding_type(blinding_set=bs)

    resp = _blinding_post(client, bs, 'hello')

    assert resp.status_code == 200

    _assert__blinding(bs, resp)


def test__ui_blinding__existing(client, faker):
    user = login(client, faker)

    b = faker.get_test_blinding_with_owner(owner=user)

    resp = _blinding_post(client, b.blinding_type.blinding_set, b.unblind_id)

    assert resp.status_code == 200

    assert Blinding.query.filter_by(
            blinding_type_id=b.blinding_type.id
        ).filter_by(
            unblind_id=b.unblind_id
        ).filter_by(
            pseudo_random_id_id=b.pseudo_random_id.id
        ).count() == 1

    dt = resp.soup.find("dt", string=b.blinding_type.name)
    assert dt is not None
    dd = dt.find_next_sibling("dd")
    assert dd.string == b.pseudo_random_id.full_code


def test__ui_blinding__not_owner(client, faker):
    user = login(client, faker)
    owner = faker.get_test_user()

    s = faker.get_test_study(owner=owner)
    bs = faker.get_test_blinding_set(study=s)

    faker.get_test_blinding_type(blinding_set=bs)

    resp = _blinding_post(client, bs, 'hello')

    assert resp.status_code == 403
