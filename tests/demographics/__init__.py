import os
from datetime import datetime
from io import BytesIO
from flask import url_for, current_app
from identity.demographics.model import DemographicsRequest, DemographicsRequestColumn
from unittest.mock import patch
from identity.demographics import (
    extract_data,
)
from identity.demographics.model import (
    DemographicsRequestCsv,
    DemographicsRequestColumnDefinition,
    DemographicsRequestData,
)
from identity.database import db
from tests import login


def assert_uploaded_file(user, filename, content, headers):
    dr = DemographicsRequest.query.filter(
        DemographicsRequest.filename == filename
        and DemographicsRequest.owner == user
    ).first()

    assert dr
    assert len(dr.columns) == len(headers)

    for h in headers:
        assert DemographicsRequestColumn.query.filter(
            DemographicsRequestColumn.demographics_request_id == dr.id
            and DemographicsRequestColumn.name == h
        ).first()

    assert os.path.isfile(dr.filepath)

    with open(dr.filepath, 'rb') as f:
        assert f.read() == content

    return dr


def assert_uploaded_file_not_exists(user, filename, content, headers):
    assert DemographicsRequest.query.filter(
        DemographicsRequest.filename == filename
        and DemographicsRequest.owner == user
    ).count() == 0


def do_create_request(client, faker, user, headers=None, data=None, extension='csv'):
    if headers is None:
        headers = faker.pylist(10, False, 'str')

    if extension == 'csv':
        content = faker.csv_string(headers=headers, data=data).encode('utf-8')
    else:
        content = faker.xslx_data(headers=headers, data=data)

    filename = faker.file_name(extension=extension)

    data = {
        'upload': (
            BytesIO(content),
            filename,
        )
    }

    response = do_upload(client, data)

    dr = DemographicsRequest.query.filter(
        DemographicsRequest.filename == filename
        and DemographicsRequest.owner == user
    ).first()

    assert response.status_code == 302
    assert response.location == url_for('ui.demographics_define_columns', id=dr.id, _external=True)

    assert dr is not None

    return dr


def do_define_columns_post(client, id, uhl_system_number_column, nhs_number_column, family_name_column, given_name_column, gender_column, dob_column, postcode_column):
    return client.post(
        url_for('ui.demographics_define_columns', id=id, _external=True),
        data = {
            'uhl_system_number_column_id': uhl_system_number_column.id if uhl_system_number_column else 0,
            'nhs_number_column_id': nhs_number_column.id if nhs_number_column else 0,
            'family_name_column_id': family_name_column.id if family_name_column else 0,
            'given_name_column_id': given_name_column.id if given_name_column else 0,
            'gender_column_id': gender_column.id if gender_column else 0,
            'dob_column_id': dob_column.id if dob_column else 0,
            'postcode_column_id': postcode_column.id if postcode_column else 0,
        },
    )


def do_upload(client, data):
    return client.post(
        url_for("ui.demographics"),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )


def do_submit(client, id):
    with patch('identity.ui.views.demographics.schedule_lookup_tasks') as mock_schedule_lookup_tasks:
        return client.post(
            url_for("ui.demographics_submit", id=id),
            buffered=True,
            content_type="multipart/form-data",
            data={'id': id},
        )

        mock_schedule_lookup_tasks.delay.assert_called_once_with(id)


def do_delete(client, id):
    return client.post(
        url_for("ui.demographics_delete", id=id),
        buffered=True,
        content_type="multipart/form-data",
        data={'id': id},
    )


def do_extract_data(id):
    with patch('identity.demographics.schedule_lookup_tasks') as mock_schedule_lookup_tasks:
        extract_data(id)

        mock_schedule_lookup_tasks.assert_called_once_with(id)


def do_upload_data_and_extract(client, faker, data, extension='csv'):
    dr = do_upload_data(client, faker, data, extension)

    do_extract_data(dr.id)

    return dr.data[0]


def do_upload_data(client, faker, data, extension='csv'):
    user = login(client, faker)

    if data is None:
        data = []
    else:
        data = [data]

    headers = ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'dob', 'postcode']

    dr = do_create_request(client, faker, user, headers, data, extension)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    do_submit(client, dr.id)

    return dr


def get_demographics_request__uploaded(faker, user):
    result = DemographicsRequestCsv(
        owner=user,
        last_updated_by_user=user,
        filename=faker.file_name(extension='csv'),
    )

    db.session.add(result)
    db.session.commit()
    return result


def get_demographics_request__awaiting_submission(faker, user):
    result = get_demographics_request__uploaded(faker, user)

    cols = {}

    for h in ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'dob', 'postcode']:
        cols[h] = DemographicsRequestColumn(
            demographics_request=result,
            name=h,
            last_updated_by_user=user,
        )

    col_def = DemographicsRequestColumnDefinition(
        demographics_request=result,
        last_updated_by_user=user,
        uhl_system_number_column=cols['uhl_system_number'],
        nhs_number_column=cols['nhs_number'],
        family_name_column=cols['family_name'],
        given_name_column=cols['given_name'],
        gender_column=cols['gender'],
        dob_column=cols['dob'],
        postcode_column=cols['postcode'],
    )

    db.session.add_all(cols.values())
    db.session.add(col_def)
    db.session.commit()
    return result


def get_demographics_request__data_extraction(faker, user):
    result = get_demographics_request__awaiting_submission(faker, user)

    result.submitted_datetime = datetime.utcnow()
    db.session.add(result)
    db.session.commit()
    return result


def get_demographics_request__pre_pmi_lookup(faker, user, row_count=1):
    result = get_demographics_request__data_extraction(faker, user)

    rows = []

    for i in range(row_count):
        p = faker.pmi_details(i)

        rows.append(DemographicsRequestData(
            row_number=i,
            demographics_request=result,
            nhs_number=p['nhs_number'],
            uhl_system_number=p['uhl_system_number'],
            family_name=p['family_name'],
            given_name=p['given_name'],
            gender=p['gender'],
            dob=p['date_of_birth'],
            postcode=p['postcode'],
        ))

    result.data_extracted_datetime = datetime.utcnow()

    db.session.add_all(rows)
    db.session.add(result)
    db.session.commit()
    return result


def get_demographics_request__spine_lookup(faker, user, row_count=1):
    result = get_demographics_request__pre_pmi_lookup(faker, user)

    result.pmi_data_pre_completed_datetime = datetime.utcnow()

    db.session.add(result)
    db.session.commit()
    return result


def get_demographics_request__post_pmi_lookup(faker, user, row_count=1):
    result = get_demographics_request__pre_pmi_lookup(faker, user, row_count=row_count)

    result.lookup_completed_datetime = datetime.utcnow()

    db.session.add(result)
    db.session.commit()
    return result
