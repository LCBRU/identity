import pytest
from flask import url_for
from identity.demographics.model import DemographicsRequest
from lbrc_flask.pytest.helpers import login, logout
from tests.demographics import (
    do_create_request,
    do_define_columns_post,
    do_submit,
    do_delete,
)
from lbrc_flask.pytest.asserts import assert__flash_messages_contains_error, assert__requires_login
from tests.ui.demographics import _assert_file_not_on_index, _remove_files


def _url(external=True, **kwargs):
    return url_for('ui.demographics_delete', _external=external, **kwargs)


@pytest.mark.skip(reason="Flask_Login is adding extra parameters to URL")
def test__get__requires_login(client, faker):
    user = login(client, faker)
    dr = do_create_request(client, faker, user)
    logout(client)

    assert__requires_login(client, _url(id=dr.id, external=False))


def test__ui_demographics_delete_get(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])
    do_submit(client, dr.id)

    response = client.get(url_for('ui.demographics_delete', id=dr.id, _external=True))
    assert response.status_code == 200

    # Do not allows others to delete
    logout(client)

    user = login(client, faker)
    response = client.get(url_for('ui.demographics_delete', id=dr.id, _external=True))
    assert response.status_code == 403

    _remove_files(dr)


def test__ui_demographics_delete_post(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])
    do_submit(client, dr.id)

    response = do_delete(client, dr.id)

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=False)

    del_dr = DemographicsRequest.query.get(dr.id)

    assert del_dr.deleted == True
    assert del_dr.deleted_datetime is not None

    _assert_file_not_on_index(client, dr.filename)

    _remove_files(dr)


def test__ui_demographics_delete_post__not_owner(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])
    do_submit(client, dr.id)

    logout(client)

    user2 = login(client, faker)
    response = do_delete(client, dr.id)

    assert response.status_code == 403

    _remove_files(dr)


def test__ui_demographics_delete_get_404(client, faker):
    user = login(client, faker)

    response = client.get(url_for('ui.demographics_delete', id=999, _external=True))

    assert response.status_code == 404


def test__ui_demographics_delete_post_404(client, faker):
    user = login(client, faker)

    response = do_delete(client, 999)

    assert response.status_code == 404


def test__ui_delete_get_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = client.get(url_for('ui.demographics_delete', id=dr.id, _external=True))

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=False)
    assert assert__flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_delete_post_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = do_delete(client, dr.id)

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=False)
    assert assert__flash_messages_contains_error(client)

    _remove_files(dr)
