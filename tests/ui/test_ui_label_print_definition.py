from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__requires_login, assert__redirect, get_and_assert_standards_modal, assert__refresh_response


def _url(external=True, **kwargs):
    return url_for('ui.label_bundle_definition', _external=external, **kwargs)


def test__get__requires_login(client, faker):
    bundle = faker.get_test_label_bundle()

    assert__requires_login(client, _url(
        id=bundle.id,
        external=False,
    ))


def test__label_print_definition__not_a_user_study(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()

    resp = client.get(_url(id=bundle.id))

    assert resp.status_code == 403


def test__label_print_definition__get(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()
    user.studies.append(bundle.study)

    resp = get_and_assert_standards_modal(client, _url(id=bundle.id))

    assert resp.status_code == 200


def test__label_print_definition__post__study_redirect(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()
    user.studies.append(bundle.study)

    data = {
        'participant_id': 'ABCDEFG',
        'count': '1',
    }

    resp = client.post(
        _url(id=bundle.id),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert__refresh_response(resp)
