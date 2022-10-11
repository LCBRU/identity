from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__requires_login, assert__redirect
from tests import lbrc_identity_get


def _url(external=True, **kwargs):
    return url_for('ui.label_print_definition', _external=external, **kwargs)


def test__get__requires_login(client, faker):
    pack = faker.get_test_label_pack()

    assert__requires_login(client, _url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
        external=False,
    ))


def test__label_print_definition__not_a_user_study(client, faker):
    user = login(client, faker)

    pack = faker.get_test_label_pack()

    resp = client.get(_url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
    ))

    assert resp.status_code == 403


def test__label_print_definition__get(client, faker):
    user = login(client, faker)

    pack = faker.get_test_label_pack()
    user.studies.append(pack.study)

    resp = lbrc_identity_get(client, _url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
    ), user)

    assert resp.status_code == 200


def test__label_print_definition__post__study_redirect(client, faker):
    user = login(client, faker)

    pack = faker.get_test_label_pack()
    user.studies.append(pack.study)

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

    pack = faker.get_test_label_pack()
    user.studies.append(pack.study)

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

    pack = faker.get_test_label_pack()
    user.studies.append(pack.study)

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
