from flask import url_for
from identity.demographics.model import DemographicsRequest
from lbrc_flask.pytest.helpers import login, logout
from tests.demographics import (
    do_create_request,
    do_define_columns_post,
    do_submit,
    do_delete,
)
from tests.ui.demographics import _assert_file_not_on_index, _remove_files
from lbrc_flask.pytest.asserts import assert__refresh_response


def _url(external=True, **kwargs):
    return url_for('ui.demographics_delete', _external=external, **kwargs)


def test__ui_demographics_delete_post(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])
    do_submit(client, dr.id)

    response = do_delete(client, dr.id)
    assert__refresh_response(response)

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


def test__ui_demographics_delete_post_404(client, faker):
    user = login(client, faker)

    response = do_delete(client, 999)

    assert response.status_code == 404


def test__ui_delete_post_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = do_delete(client, dr.id)

    assert__refresh_response(response)

    _remove_files(dr)
