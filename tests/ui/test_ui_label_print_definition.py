from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__requires_login, assert__redirect, assert__refresh_response
from tests import lbrc_identity_get_modal


def _url(external=True, **kwargs):
    return url_for('ui.label_bundle_definition', _external=external, **kwargs)


def test__get__requires_login(client, faker):
    bundle = faker.get_test_label_bundle()

    assert__requires_login(client, _url(
        referrer='study',
        id=bundle.id,
        external=False,
    ))


def test__label_print_definition__not_a_user_study(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()

    resp = client.get(_url(
        referrer='study',
        id=bundle.id,
    ))

    assert resp.status_code == 403


def test__label_print_definition__get(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()
    user.studies.append(bundle.study)

    resp = lbrc_identity_get_modal(client, _url(
        referrer='study',
        id=bundle.id,
    ), user)

    assert resp.status_code == 200


def test__label_print_definition__post__study_redirect(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()
    user.studies.append(bundle.study)

    data = {
        'participant_id': 'ABCDEFG',
        'count': 1,
    }

    resp = client.post(
        _url(
            referrer='study',
            id=bundle.id,
        ),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert__refresh_response(resp)


def test__label_print_definition__post__labels_redirect(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()
    user.studies.append(bundle.study)

    data = {
        'participant_id': 'ABCDEFG',
        'count': 1,
    }

    resp = client.post(
        _url(
            referrer='labels',
            id=bundle.id,
        ),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert__refresh_response(resp)


def test__label_print_definition__post__no_id_given(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()
    user.studies.append(bundle.study)

    data = {
        'participant_id': '',
        'count': 1,
    }

    resp = client.post(
        _url(
            referrer='labels',
            id=bundle.id,
        ),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert resp.status_code == 200
