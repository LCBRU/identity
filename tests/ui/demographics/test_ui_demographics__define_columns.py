import pytest
import re
from flask import url_for
from identity.demographics.model import DemographicsRequest
from lbrc_flask.pytest.helpers import login, logout
from tests.demographics import (
    do_create_request,
    do_define_columns_post,
    do_submit,
    do_delete,
)
from lbrc_flask.pytest.asserts import (
    assert__flash_messages_contains_error,
    assert__requires_login,
    assert__redirect
)
from tests.ui.demographics import AWAITING_SUBMISSION, _remove_files, _assert_uploaded_file_on_index
from lbrc_flask.pytest.asserts import get_and_assert_standards_modal


def _url(external=True, **kwargs):
    return url_for('ui.demographics_define_columns', _external=external, **kwargs)


def test__get__requires_login(client, faker):
    user = login(client, faker)
    dr = do_create_request(
        client,
        faker,
        user,
        headers=faker.column_headers(10),
    )
    logout(client)

    assert__requires_login(client, _url(id=dr.id, external=False))


def test__ui_demographics_define_columns_get(client, faker):
    user = login(client, faker)
    headers = faker.column_headers(10)

    dr = do_create_request(client, faker, user, headers=headers)

    response = get_and_assert_standards_modal(client, _url(id=dr.id))
    assert response.status_code == 200

    print(response.soup.prettify())

    for sid in ['nhs_number_column_id', 'family_name_column_id', 'given_name_column_id', 'gender_column_id', 'dob_column_id', 'postcode_column_id']:
        print(f'{sid=}')
        select = response.soup.find('select', id=sid)
        assert select is not None

        for o in [None, *headers]:
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
        assert__redirect(response, 'ui.demographics_submit', id=dr.id)

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

    assert__redirect(response, 'ui.demographics_submit', id=dr.id)

    response = client.get(url_for('ui.demographics_define_columns', id=dr.id, _external=False))

    for i, name in enumerate(['uhl_system_number_column_id', 'nhs_number_column_id', 'family_name_column_id', 'given_name_column_id', 'gender_column_id', 'dob_column_id', 'postcode_column_id']):
        select = response.soup.find('select', {'name': name})
        assert select is not None
        option = select.find('option', {"value": dr.columns[i].id})
        assert option is not None
        assert 'selected' in option.attrs

    _assert_uploaded_file_on_index(client, dr.filename, dr.id, AWAITING_SUBMISSION)

    _remove_files(dr)


def test__ui_demographics_define_columns_get_404(client, faker):
    user = login(client, faker)

    response = client.get(url_for('ui.demographics_define_columns', id=999, _external=False))

    assert response.status_code == 404


def test__ui_demographics_define_columns_post_404(client, faker):
    user = login(client, faker)

    response = do_define_columns_post(client, 999, None, None, None, None, None, None, None)

    assert response.status_code == 404


def test__ui_demographics_define_columns_get_submitted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])
    do_submit(client, dr.id)
    response = client.get(url_for('ui.demographics_define_columns', id=dr.id, _external=True))

    assert__redirect(response, 'ui.demographics')

    assert assert__flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_define_columns_post_submitted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])
    do_submit(client, dr.id)
    response = do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    assert__redirect(response, 'ui.demographics')

    assert assert__flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_define_columns_get_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = client.get(url_for('ui.demographics_define_columns', id=dr.id, _external=True))

    assert__redirect(response, 'ui.demographics')

    assert assert__flash_messages_contains_error(client)

    _remove_files(dr)


def test__ui_demographics_define_columns_post_deleted(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_delete(client, dr.id)
    response = do_define_columns_post(client, dr.id, None, None, None, None, None, None, None)

    assert__redirect(response, 'ui.demographics')

    assert assert__flash_messages_contains_error(client)

    _remove_files(dr)
