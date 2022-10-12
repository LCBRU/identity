import pytest
from io import BytesIO
from flask import url_for
from lbrc_flask.database import db
from lbrc_flask.pytest.helpers import login
from tests.demographics import (
    assert_uploaded_file,
    assert_uploaded_file_not_exists,
    do_upload,
)
from lbrc_flask.pytest.asserts import assert__flash_messages_contains_error, assert__requires_login, assert__redirect
from tests.ui.demographics import AWAITING_DEFINE_COLUMNS, _assert_uploaded_file_on_index, _remove_files


def _url(external=True, **kwargs):
    return url_for('ui.demographics', _external=external, **kwargs)


def test__get__requires_login(client):
    assert__requires_login(client, _url(external=False))


def test__ui_demographics_upload_csv(client, faker):
    headers = faker.column_headers(10)

    _test__ui_demographics_upload(
        client,
        faker,
        content=faker.csv_string(headers=headers).encode('utf-8'),
        extension='csv',
        headers=headers,
    )


def test__ui_demographics_upload_csv_invalid(client, faker):
    headers = faker.column_headers(10)

    _test__ui_demographics_upload_error(
        client,
        faker,
        content=faker.xslx_data(headers=headers),
        extension='csv',
        headers=headers,
    )


def test__ui_demographics_upload_xslx(client, faker):
    headers = faker.column_headers(10)

    _test__ui_demographics_upload(
        client,
        faker,
        content=faker.xslx_data(headers=headers),
        extension='xlsx',
        headers=headers,
    )


def test__ui_demographics_upload_xslx_invalid(client, faker):
    headers = faker.column_headers(10)

    _test__ui_demographics_upload_error(
        client,
        faker,
        content=faker.csv_string(headers=headers).encode('utf-8'),
        extension='xlsx',
        headers=headers,
    )


def test__ui_demographics_upload_csv__skip_pmi(client, faker):
    headers = faker.column_headers(10)

    _test__ui_demographics_upload(
        client,
        faker,
        content=faker.csv_string(headers=headers).encode('utf-8'),
        extension='csv',
        headers=headers,
        skip_pmi=True,
    )


def test__ui_demographics_upload_xslx__skip_pmi(client, faker):
    headers = faker.column_headers(10)

    _test__ui_demographics_upload(
        client,
        faker,
        content=faker.xslx_data(headers=headers),
        extension='xlsx',
        headers=headers,
        skip_pmi=True,
    )


def _test__ui_demographics_upload(client, faker, content, extension, headers, skip_pmi=False):
    user = login(client, faker)

    filename = faker.file_name(extension=extension)

    data = {
        'upload': (
            BytesIO(content),
            filename,
        )
    }

    if skip_pmi:
        data['skip_pmi'] = 'True'

    response = do_upload(client, data)

    dr = assert_uploaded_file(user, filename, content, headers, skip_pmi)

    assert__redirect(response, 'ui.demographics_define_columns', id=dr.id)

    _assert_uploaded_file_on_index(
        client,
        filename,
        dr.id,
        AWAITING_DEFINE_COLUMNS,
    )

    _remove_files(dr)


def _test__ui_demographics_upload_error(client, faker, content, extension, headers):
    user = login(client, faker)

    filename = faker.file_name(extension=extension)

    data = {
        'upload': (
            BytesIO(content),
            filename,
        )
    }

    response = do_upload(client, data)

    assert_uploaded_file_not_exists(user, filename, content, headers)

    assert__redirect(response, 'ui.demographics')

    assert assert__flash_messages_contains_error(client)
