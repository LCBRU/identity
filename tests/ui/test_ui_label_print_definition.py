import pytest
from flask import url_for
from identity.printing.model import LabelPack
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__requires_login, assert__redirect
from tests import lbrc_identity_get


def _url(external=True, **kwargs):
    return url_for('ui.label_print_definition', _external=external, **kwargs)


@pytest.mark.skip(reason="Flask_Login is adding extra parameters to URL")
def test__get__requires_login(client):
    pack = LabelPack.query.filter_by(type='CardiometPack').one()

    assert__requires_login(client, _url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
        external=False,
    ))


def test__label_print_definition__not_a_user_study(client, faker):
    user = login(client, faker)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    resp = client.get(_url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
    ))

    assert resp.status_code == 403


def test__label_print_definition__get(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    resp = lbrc_identity_get(client, _url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
    ), user)

    assert resp.status_code == 200


def test__label_print_definition__post__study_redirect(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    data = {
        'participant_id': 'ABCDEFG'
    }

    resp = client.post(
        _url(
            referrer='study',
            study_id=pack.study_id,
            pack_name=pack.type,
            count=1,
        ),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert__redirect(resp, 'ui.study', id=pack.study_id)


def test__label_print_definition__post__labels_redirect(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    data = {
        'participant_id': 'ABCDEFG'
    }

    resp = client.post(
        _url(
            referrer='labels',
            study_id=pack.study_id,
            pack_name=pack.type,
            count=1,
        ),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert__redirect(resp, 'ui.labels')


def test__label_print_definition__post__no_id_given(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    data = {
        'participant_id': ''
    }

    resp = client.post(
        _url(
            referrer='labels',
            study_id=pack.study_id,
            pack_name=pack.type,
            count=1,
        ),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert resp.status_code == 200
