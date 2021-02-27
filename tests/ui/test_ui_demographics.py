import contextlib
import pytest
import os
import re
from datetime import datetime
from io import BytesIO
from flask import url_for
from identity.demographics.model import DemographicsRequest, DemographicsRequestColumn
from lbrc_flask.database import db
from tests import flash_messages_contains_error
from lbrc_flask.pytest.helpers import login, logout
from tests.demographics import (
    assert_uploaded_file,
    assert_uploaded_file_not_exists,
    do_create_request,
    do_define_columns_post,
    do_upload,
    do_submit,
    do_delete,
)

AWAITING_DEFINE_COLUMNS = 'AWAITING_DEFINE_COLUMNS'
AWAITING_SUBMISSION = 'AWAITING_SUBMISSION'
AWAITING_COMPLETION = 'AWAITING_COMPLETION'
RESULT_CREATED = 'RESULT_CREATED'


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

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics_define_columns', id=dr.id, _external=True)

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

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)


def test__ui_demographics_define_columns_get(client, faker):
    user = login(client, faker)
    headers = faker.column_headers(10)

    dr = do_create_request(client, faker, user, headers=headers)

    response = client.get(url_for('ui.demographics_define_columns', id=dr.id, _external=True))
    assert response.status_code == 200

    for sid in ['nhs_number_column_id', 'family_name_column_id', 'given_name_column_id', 'gender_column_id', 'dob_column_id', 'postcode_column_id']:
        select = response.soup.find('select', id=sid)
        assert select is not None

        for o in ['', *headers]:
            assert select.find('option', string=o) is not None

    _remove_files(dr)


def test__ui_demographics_define_columns_get__not_owner(client, faker):
    user = login(client, faker)
    headers = faker.column_headers(10)

    dr = do_create_request(client, faker, user, headers=headers)

    logout(client)

    user2 = login(client, faker)
    response = client.get(url_for('ui.demographics_define_columns', id=dr.id, _external=True))

    assert response.status_code == 403

    _remove_files(dr)


@pytest.mark.parametrize(
    "uhl_system_number_column_idx, nhs_column_idx,family_name_idx,given_name_idx,gender_idx,dob_idx,postcode_idx,is_valid",
    [
        (0, -1, -1, -1, -1, -1, -1, True),
        (-1, 0, -1, -1, -1, -1, -1, False),
        (-1, -1, 0, -1, -1, -1, -1, False),
        (-1, -1, -1, 0, -1, -1, -1, False),
        (-1, -1, -1, -1, 0, -1, -1, False),
        (-1, -1, -1, -1, -1, 0, -1, False),
        (-1, -1, -1, -1, -1, -1, 0, False),
        (-1, 0, -1, -1, -1, 1, -1, True),
        (-1, -1, 0, 1, 2, 3, 4, True),
    ],
)
def test__ui_demographics_define_columns_post(client, faker, uhl_system_number_column_idx, nhs_column_idx, family_name_idx, given_name_idx, gender_idx, dob_idx, postcode_idx, is_valid):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)

    ex_uhl_system_number_column = dr.columns[uhl_system_number_column_idx] if uhl_system_number_column_idx >= 0 else None
    ex_nhs_number_column = dr.columns[nhs_column_idx] if nhs_column_idx >= 0 else None
    ex_family_name_column = dr.columns[family_name_idx] if family_name_idx >= 0 else None
    ex_given_name_column = dr.columns[given_name_idx] if given_name_idx >= 0 else None
    ex_gender_column = dr.columns[gender_idx] if gender_idx >= 0 else None
    ex_dob_column = dr.columns[dob_idx] if dob_idx >= 0 else None
    ex_postcode_column = dr.columns[postcode_idx] if postcode_idx >= 0 else None

    response = do_define_columns_post(client, dr.id, ex_uhl_system_number_column, ex_nhs_number_column, ex_family_name_column, ex_given_name_column, ex_gender_column, ex_dob_column, ex_postcode_column)

    if (not is_valid):
        assert response.status_code == 200
        assert response.soup.find(string=re.compile("Column specification is invalid")) is not None
    else:
        assert response.status_code == 302
        assert response.location == url_for('ui.demographics_submit', id=dr.id, _external=True)

        dr = DemographicsRequest.query.get(dr.id)
        
        assert dr.column_definition is not None

        if ex_uhl_system_number_column:
            assert dr.column_definition.uhl_system_number_column_id == ex_uhl_system_number_column.id
            assert dr.column_definition.uhl_system_number_column == ex_uhl_system_number_column
        else:
            assert dr.column_definition.uhl_system_number_column_id is None
            assert dr.column_definition.uhl_system_number_column is None

        if ex_nhs_number_column:
            assert dr.column_definition.nhs_number_column_id == ex_nhs_number_column.id
            assert dr.column_definition.nhs_number_column == ex_nhs_number_column
        else:
            assert dr.column_definition.nhs_number_column_id is None
            assert dr.column_definition.nhs_number_column is None

        if ex_family_name_column:
            assert dr.column_definition.family_name_column_id == ex_family_name_column.id
            assert dr.column_definition.family_name_column == ex_family_name_column
        else:
            assert dr.column_definition.family_name_column_id is None
            assert dr.column_definition.family_name_column is None

        if ex_given_name_column:
            assert dr.column_definition.given_name_column_id == ex_given_name_column.id
            assert dr.column_definition.given_name_column == ex_given_name_column
        else:
            assert dr.column_definition.given_name_column_id is None
            assert dr.column_definition.given_name_column is None

        if ex_gender_column:
            assert dr.column_definition.gender_column_id == ex_gender_column.id
            assert dr.column_definition.gender_column == ex_gender_column
        else:
            assert dr.column_definition.gender_column_id is None
            assert dr.column_definition.gender_column is None

        if ex_dob_column:
            assert dr.column_definition.dob_column_id == ex_dob_column.id
            assert dr.column_definition.dob_column == ex_dob_column
        else:
            assert dr.column_definition.dob_column_id is None
            assert dr.column_definition.dob_column is None

        if ex_postcode_column:
            assert dr.column_definition.postcode_column_id == ex_postcode_column.id
            assert dr.column_definition.postcode_column == ex_postcode_column
        else:
            assert dr.column_definition.postcode_column_id is None
            assert dr.column_definition.postcode_column is None

        _assert_uploaded_file_on_index(client, dr.filename, dr.id, AWAITING_SUBMISSION)

    _remove_files(dr)


def test__ui_demographics_define_columns_post__not_owner(client, faker):
    user = login(client, faker)
    headers = faker.column_headers(10)

    dr = do_create_request(client, faker, user, headers=headers)

    logout(client)

    user2 = login(client, faker)

    response = client.post(
        url_for('ui.demographics_define_columns', id=dr.id, _external=True),
        data = {
            'uhl_system_number_column_id': 0,
            'nhs_number_column_id': 0,
            'family_name_column_id': 0,
            'given_name_column_id': 0,
            'gender_column_id': 0,
            'dob_column_id': 0,
            'postcode_column_id': 0,
        },
    )

    assert response.status_code == 403

    _remove_files(dr)


def test__ui_demographics_define_columns_update(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    response = do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics_submit', id=dr.id, _external=True)

    response = client.get(url_for('ui.demographics_define_columns', id=dr.id, _external=True))

    for i, name in enumerate(['uhl_system_number_column_id', 'nhs_number_column_id', 'family_name_column_id', 'given_name_column_id', 'gender_column_id', 'dob_column_id', 'postcode_column_id']):
        select = response.soup.find('select', {'name': name})
        assert select is not None
        option = select.find('option', {"value": dr.columns[i].id})
        assert option is not None
        assert 'selected' in option.attrs

    _assert_uploaded_file_on_index(client, dr.filename, dr.id, AWAITING_SUBMISSION)

    _remove_files(dr)


def test__ui_demographics_submit_get(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    response = client.get(url_for('ui.demographics_submit', id=dr.id, _external=True))
    assert response.status_code == 200

    _remove_files(dr)


def test__ui_demographics_submit_get__not_owner(client, faker):
    user = login(client, faker)
    headers = faker.column_headers(10)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    logout(client)

    user2 = login(client, faker)
    response = client.get(url_for('ui.demographics_submit', id=dr.id, _external=True))
    assert response.status_code == 403

    _remove_files(dr)


def test__ui_demographics_submit_post(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    response = do_submit(client, dr.id)

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)

    _assert_uploaded_file_on_index(client, dr.filename, dr.id, AWAITING_COMPLETION)

    _remove_files(dr)


def test__ui_demographics_submit_post__not_owner(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    logout(client)

    user2 = login(client, faker)
    response = do_submit(client, dr.id)
    assert response.status_code == 403

    _remove_files(dr)


def test__ui_demographics_no_result_created(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    response = do_submit(client, dr.id)

    response = client.get(url_for('ui.demographics_download_result', id=dr.id, _external=True))
    assert response.status_code == 404

    _remove_files(dr)


def test__ui_demographics_result_created__download(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    response = do_submit(client, dr.id)

    dr.result_created_datetime = datetime.utcnow()

    db.session.add(dr)
    db.session.commit()

    contents = faker.text()

    with open(dr.result_filepath, "w") as f:
        f.write(contents)
        
    _assert_uploaded_file_on_index(client, dr.filename, dr.id, RESULT_CREATED)

    response = client.get(url_for('ui.demographics_download_result', id=dr.id, _external=True))
    assert response.status_code == 200
    assert response.get_data().decode("utf8") == contents

    dr = DemographicsRequest.query.get(dr.id)
    assert dr.result_downloaded_datetime is not None
    assert dr.result_downloaded == True

    # Do not allows others to download
    logout(client)

    user = login(client, faker)
    response = client.get(url_for('ui.demographics_download_result', id=dr.id, _external=True))
    assert response.status_code == 403

    _remove_files(dr)


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
    assert response.location == url_for('ui.demographics', _external=True)

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


def test__ui_demographics_define_columns_get_404(client, faker):
    user = login(client, faker)

    response = client.get(url_for('ui.demographics_define_columns', id=999, _external=True))

    assert response.status_code == 404


def test__ui_demographics_define_columns_post_404(client, faker):
    user = login(client, faker)

    response = do_define_columns_post(client, 999, None, None, None, None, None, None, None)

    assert response.status_code == 404


def test__ui_demographics_submit_get_404(client, faker):
    user = login(client, faker)

    response = client.get(url_for('ui.demographics_submit', id=999, _external=True))

    assert response.status_code == 404


def test__ui_demographics_submit_post_404(client, faker):
    user = login(client, faker)

    response = do_submit(client, 999)

    assert response.status_code == 404


def test__ui_demographics_delete_get_404(client, faker):
    user = login(client, faker)

    response = client.get(url_for('ui.demographics_delete', id=999, _external=True))

    assert response.status_code == 404


def test__ui_demographics_delete_post_404(client, faker):
    user = login(client, faker)

    response = do_delete(client, 999)

    assert response.status_code == 404


def test__ui_demographics_define_columns_get_submitted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])
    do_submit(client, dr.id)
    response = client.get(url_for('ui.demographics_define_columns', id=dr.id, _external=True))

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_define_columns_post_submitted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])
    do_submit(client, dr.id)
    response = do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_define_columns_get_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = client.get(url_for('ui.demographics_define_columns', id=dr.id, _external=True))

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_define_columns_post_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = do_define_columns_post(client, dr.id, None, None, None, None, None, None, None)

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_submit_get_submitted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_submit(client, dr.id)
    response = client.get(url_for('ui.demographics_submit', id=dr.id, _external=True))

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_submit_post_submitted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_submit(client, dr.id)
    response = do_submit(client, dr.id)

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_submit_get_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = do_submit(client, dr.id)

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_submit_post_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = do_submit(client, dr.id)

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_delete_get_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = client.get(url_for('ui.demographics_delete', id=dr.id, _external=True))

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_delete_post_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = do_delete(client, dr.id)

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics', _external=True)
    assert flash_messages_contains_error(client)

    _remove_files(dr)


def _assert_uploaded_file_on_index(client, filename, id, status):
    response = client.get(url_for('ui.demographics'))

    assert response.soup.find(string=re.compile(filename)) is not None

    if status == AWAITING_DEFINE_COLUMNS:
        assert response.soup.find('a', href=url_for('ui.demographics_define_columns', id=id)) is not None
        assert response.soup.find('a', href=url_for('ui.demographics_submit', id=id)) is None
        assert response.soup.find('a', href=url_for('ui.demographics_delete', id=id)) is not None
    elif status == AWAITING_SUBMISSION:
        assert response.soup.find('a', href=url_for('ui.demographics_define_columns', id=id)) is not None
        assert response.soup.find('a', href=url_for('ui.demographics_submit', id=id)) is not None
        assert response.soup.find('a', href=url_for('ui.demographics_delete', id=id)) is not None
    elif status == AWAITING_COMPLETION:
        assert response.soup.find('a', href=url_for('ui.demographics_define_columns', id=id)) is None
        assert response.soup.find('a', href=url_for('ui.demographics_submit', id=id)) is None
        assert response.soup.find('a', href=url_for('ui.demographics_delete', id=id)) is not None
    elif status == RESULT_CREATED:
        assert response.soup.find('a', href=url_for('ui.demographics_define_columns', id=id)) is None
        assert response.soup.find('a', href=url_for('ui.demographics_submit', id=id)) is None
        assert response.soup.find('a', href=url_for('ui.demographics_delete', id=id)) is not None
        assert response.soup.find('a', href=url_for('ui.demographics_download_result', id=id)) is not None


def _assert_file_not_on_index(client, filename):
    response = client.get(url_for('ui.demographics'))

    assert response.soup.find('h1', string=filename) is None


def _remove_files(dr):
    with contextlib.suppress(FileNotFoundError):
        os.remove(dr.filepath)
        os.remove(dr.result_filepath)
