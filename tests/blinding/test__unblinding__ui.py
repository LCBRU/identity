import re
from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.database import db
from lbrc_flask.pytest.asserts import assert__error__message


def _url(study_id, external=True):
    return url_for('ui.unblinding', id=study_id, _external=external)


def _unblinding_post(client, blinding_set, id):
    return client.post(
        _url(study_id=blinding_set.study.id, external=False),
        data={'id': id},
        follow_redirects=True,
    )


def test__ui_unblinding__existing(client, faker):
    user = login(client, faker)

    b = faker.get_test_blinding_with_owner(owner=user)

    resp = _unblinding_post(client, b.blinding_type.blinding_set, b.pseudo_random_id.full_code)

    assert resp.status_code == 200
    assert__error__message(resp.soup, f'is unblinded to "{b.unblind_id}"')


def test__ui_unblinding__not_existing(client, faker):
    user = login(client, faker)

    b = faker.get_test_blinding_with_owner(owner=user)

    resp = _unblinding_post(client, b.blinding_type.blinding_set, '1234567')

    assert resp.status_code == 200
    assert__error__message(resp.soup, 'Blind ID "1234567" not found for study')


def test__ui_unblinding__not_owner(client, faker):
    user = login(client, faker)
    owner = faker.get_test_user()

    b = faker.get_test_blinding_with_owner(owner=owner)

    resp = _unblinding_post(client, b.blinding_type.blinding_set, b.pseudo_random_id.full_code)

    assert resp.status_code == 403
