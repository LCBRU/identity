import os
from datetime import datetime, UTC
from io import BytesIO
from flask import url_for
from identity.demographics.model import DemographicsRequest, DemographicsRequestColumn
from unittest.mock import patch
from identity.demographics import extract_data
from time import sleep
from lbrc_flask.database import db
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__redirect
from sqlalchemy import select, func


def assert_uploaded_file(user, filename, content, headers):
    dr = db.session.execute(
        select(DemographicsRequest)
        .where(DemographicsRequest.filename == filename)
        .where(DemographicsRequest.owner == user)
    ).scalars().first()

    assert dr
    assert len(dr.columns) == len(headers)

    for h in headers:
        assert db.session.execute(
            select(DemographicsRequestColumn)
            .where(DemographicsRequestColumn.demographics_request_id == dr.id)
            .where(DemographicsRequestColumn.name == h)
        )

    assert os.path.isfile(dr.filepath)

    with open(dr.filepath, 'rb') as f:
        assert f.read() == content

    return dr


def assert_uploaded_file_not_exists(user, filename, content, headers):
    assert db.session.execute(
        select(func.count(1))
        .where(DemographicsRequest.filename == filename)
        .where(DemographicsRequest.owner == user)
    ).scalar_one() == 0


def do_create_request(client, faker, user, headers=None, data=None, extension='csv'):
    if headers is None:
        headers = [chr(65 + i) * 10 for i in range(10)]

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

    sleep(1)

    response = do_upload(client, data)

    dr = db.session.execute(
        select(DemographicsRequest)
        .where(DemographicsRequest.filename == filename)
        .where(DemographicsRequest.owner == user)
    ).scalars().first()

    assert__redirect(response, 'ui.demographics_define_columns', id=dr.id)

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
        url_for("ui.demographics_upload"),
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


class DemographicsTestHelper():

    def __init__(self, faker, user, extension='csv', row_count=1, include_data_errors=False, column_headings=None, find_pre_pmi_details=True, find_post_pmi_details=True):
        self._faker = faker
        self._user = user
        self._extension = extension
        self._row_count = row_count
        self._include_data_errors = include_data_errors
        self._filename = self._faker.file_name(extension=self._extension)
        self._find_pre_pmi_details = find_pre_pmi_details
        self._find_post_pmi_details = find_post_pmi_details

        if column_headings is None:
            self._column_headings = ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'date_of_birth', 'postcode']
        else:
            self._column_headings = column_headings

        self._person_details = []

        for _ in range(self._row_count):
            p = self._faker.person_details()
            p['expected_message'] = self._faker.pystr(min_chars=None, max_chars=20)
            self._person_details.append(p)

    def get_request_person_details(self):
        result = []

        for p in self._person_details:
            result.append({key: value for key, value in p.items() if key in self._column_headings})
        
        return result


    def get_demographics_request__uploaded(self):
        result = self._faker.demographics_request().get(
            save=True,
            owner=self._user,
            last_updated_by_user=self._user,
            filename=self._filename,
            extension=self._extension,
        )
        self._faker.demographics_request().create_file(
            result,
            headers=self._column_headings,
            data=self._person_details,
        )

        return result


    def get_demographics_request__columns_defined(self):
        result = self.get_demographics_request__uploaded()

        cols = {}

        for h in self._column_headings:
            cols[h] = self._faker.demographics_request_column().get(
                save=True,
                demographics_request=result,
                name=h,
                last_updated_by_user=self._user,
            )

        self._faker.demographics_request_column_definition().get(
            save=True,
            demographics_request=result,
            last_updated_by_user=self._user,
            uhl_system_number_column=cols.get('uhl_system_number'),
            nhs_number_column=cols.get('nhs_number'),
            family_name_column=cols.get('family_name'),
            given_name_column=cols.get('given_name'),
            gender_column=cols.get('gender'),
            dob_column=cols.get('date_of_birth'),
            postcode_column=cols.get('postcode'),
        )

        return result


    def get_demographics_request__submitted(self):
        result = self.get_demographics_request__columns_defined()

        result.submitted_datetime = datetime.now(UTC)
        db.session.add(result)
        db.session.commit()
        return result


    def get_demographics_request__request_data_extracted(self):
        result = self.get_demographics_request__submitted()

        for i, p in enumerate(self.get_request_person_details()):
            self._faker.demographics_request_data().get(
                save=True,
                row_number=i,
                demographics_request=result,
                nhs_number=p.get('nhs_number'),
                uhl_system_number=p.get('uhl_system_number'),
                family_name=p.get('family_name'),
                given_name=p.get('given_name'),
                gender=p.get('gender'),
                dob=str(p.get('date_of_birth')),
                postcode=p.get('postcode'),
            )

        result.data_extracted_datetime = datetime.now(UTC)

        db.session.add(result)
        db.session.commit()
        return result


    def get_demographics_request__with_pmi_details(self):
        result = self.get_demographics_request__request_data_extracted()

        if self._find_pre_pmi_details:
            for drd, p in zip(result.data, self._person_details):
                self._faker.demographics_request_pmi_data().get(
                    save=True,
                    demographics_request_data=drd,
                    nhs_number=p['nhs_number'],
                    uhl_system_number=p['uhl_system_number'],
                    family_name=p['family_name'],
                    given_name=p['given_name'],
                    gender=p['gender'],
                    date_of_birth=p['date_of_birth'],
                    date_of_death=p['date_of_death'],
                    postcode=p['postcode'],
                )

        result.pmi_data_pre_completed_datetime = datetime.now(UTC)

        db.session.add(result)
        db.session.commit()
        return result


    def get_demographics_request__download(self):
        result = self.get_demographics_request__with_pmi_details()

        result.create_result()
        result.result_created_datetime = datetime.now(UTC)
        db.session.add(result)
        db.session.commit()

        return result
