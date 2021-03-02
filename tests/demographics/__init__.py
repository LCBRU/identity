import os
import csv
import xlwt
from openpyxl import Workbook
from datetime import datetime
from io import BytesIO
from flask import url_for
from identity.demographics.model import DemographicsRequest, DemographicsRequestColumn
from unittest.mock import patch
from identity.demographics import (
    extract_data,
)
from identity.demographics.model import (
    DemographicsRequestCsv,
    DemographicsRequestXlsx,
    DemographicsRequestExcel97,
    DemographicsRequestColumnDefinition,
    DemographicsRequestData,
    DemographicsRequestPmiData,
    DemographicsRequestDataResponse,
    DemographicsRequestDataMessage,
)
from lbrc_flask.database import db
from lbrc_flask.pytest.helpers import login


def assert_uploaded_file(user, filename, content, headers, skip_pmi):
    dr = DemographicsRequest.query.filter(
        DemographicsRequest.filename == filename
        and DemographicsRequest.owner == user
    ).first()

    assert dr
    assert len(dr.columns) == len(headers)
    assert dr.skip_pmi == skip_pmi

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

    def __init__(self, faker, user, extension='csv', row_count=1, include_data_errors=False, column_headings=None, find_pre_pmi_details=True, find_post_pmi_details=True, skip_pmi=False):
        self._faker = faker
        self._user = user
        self._extension = extension
        self._row_count = row_count
        self._include_data_errors = include_data_errors
        self._filename = self._faker.file_name(extension=self._extension)
        self._find_pre_pmi_details = find_pre_pmi_details
        self._find_post_pmi_details = find_post_pmi_details
        self._skip_pmi = skip_pmi

        if column_headings is None:
            self._column_headings = ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'date_of_birth', 'postcode']
        else:
            self._column_headings = column_headings

        self._person_details = []

        for _ in range(self._row_count):
            p = self._faker.person_details()
            p['expected_message'] = self._faker.pystr(min_chars=None, max_chars=20)
            self._person_details.append(p)

    def get_input_details(self):
        result = []

        for p in self._person_details:
            result.append({key: value for key, value in p.items() if key in self._column_headings})
        
        return result


    def get_demographics_request__uploaded(self):

        if self._extension == 'csv':
            return self._create_csv_file()
        elif self._extension == 'xlsx':
            return self._create_xlsx_file()
        elif self._extension == 'xls':
            return self._create_xls_file()


    def get_demographics_request__awaiting_submission(self):
        result = self.get_demographics_request__uploaded()

        cols = {}

        for h in self._column_headings:
            cols[h] = DemographicsRequestColumn(
                demographics_request=result,
                name=h,
                last_updated_by_user=self._user,
            )

        col_def = DemographicsRequestColumnDefinition(
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

        db.session.add_all(cols.values())
        db.session.add(col_def)
        db.session.commit()
        return result


    def get_demographics_request__data_extraction(self):
        result = self.get_demographics_request__awaiting_submission()

        result.submitted_datetime = datetime.utcnow()
        db.session.add(result)
        db.session.commit()
        return result


    def get_demographics_request__pre_pmi_lookup(self):
        result = self.get_demographics_request__data_extraction()

        rows = []

        for i, p in enumerate(self.get_input_details()):
            rows.append(DemographicsRequestData(
                row_number=i,
                demographics_request=result,
                nhs_number=p.get('nhs_number'),
                uhl_system_number=p.get('uhl_system_number'),
                family_name=p.get('family_name'),
                given_name=p.get('given_name'),
                gender=p.get('gender'),
                dob=p.get('date_of_birth'),
                postcode=p.get('postcode'),
            ))

        result.data_extracted_datetime = datetime.utcnow()

        db.session.add_all(rows)
        db.session.add(result)
        db.session.commit()
        return result


    def get_demographics_request__spine_lookup(self):
        result = self.get_demographics_request__pre_pmi_lookup()

        rows = []

        if self._find_pre_pmi_details:
            for drd, p in zip(result.data, self._person_details):
                rows.append(DemographicsRequestPmiData(
                    demographics_request_data=drd,
                    nhs_number=p['nhs_number'],
                    uhl_system_number=p['uhl_system_number'],
                    family_name=p['family_name'],
                    given_name=p['given_name'],
                    gender=p['gender'],
                    date_of_birth=p['date_of_birth'],
                    date_of_death=p['date_of_death'],
                    postcode=p['postcode'],
                ))

        result.pmi_data_pre_completed_datetime = datetime.utcnow()

        db.session.add_all(rows)
        db.session.add(result)
        db.session.commit()
        return result


    def get_demographics_request__post_pmi_lookup(self):
        result = self.get_demographics_request__spine_lookup()

        rows = []

        for drd, p in zip(result.data, self._person_details):
            rows.append(DemographicsRequestDataResponse(
                demographics_request_data=drd,
                title=p['title'],
                forename=p['given_name'],
                middlenames=p['middle_name'],
                lastname=p['family_name'],
                sex=p['gender'],
                postcode=p['postcode'],
                address=p['address'],
                date_of_birth=p['date_of_birth'],
                date_of_death=p['date_of_death'],
                is_deceased=p['is_deceased'],
                current_gp_practice_code=p['current_gp_practice_code'],
            ))

            if self._include_data_errors:
                rows.append(DemographicsRequestDataMessage(
                    demographics_request_data=drd,
                    type='error',
                    source='TEST',
                    scope='DATA',
                    message=p['expected_message'],
                ))

        result.lookup_completed_datetime = datetime.utcnow()

        db.session.add_all(rows)
        db.session.add(result)
        db.session.commit()
        return result


    def get_demographics_request__create_results(self):
        result = self.get_demographics_request__post_pmi_lookup()

        rows = []

        if self._find_post_pmi_details:
            for drd, p in zip(result.data, self._person_details):
                rows.append(DemographicsRequestPmiData(
                    demographics_request_data=drd,
                    nhs_number=p['nhs_number'],
                    uhl_system_number=p['uhl_system_number'],
                    family_name=p['family_name'],
                    given_name=p['given_name'],
                    gender=p['gender'],
                    date_of_birth=p['date_of_birth'],
                    date_of_death=p['date_of_death'],
                    postcode=p['postcode'],
                ))

        result.pmi_data_post_completed_datetime = datetime.utcnow()

        db.session.add_all(rows)
        db.session.add(result)
        db.session.commit()
        return result


    def get_demographics_request__download(self):
        result = self.get_demographics_request__create_results()

        result.create_result()
        result.result_created_datetime = datetime.utcnow()
        db.session.add(result)
        db.session.commit()

        return result


    def _create_csv_file(self):
        result = DemographicsRequestCsv(
            owner=self._user,
            last_updated_by_user=self._user,
            filename=self._filename,
            skip_pmi=self._skip_pmi,
        )

        db.session.add(result)
        db.session.commit()

        os.makedirs(os.path.dirname(result.filepath), exist_ok=True)

        with open(result.filepath, 'w') as csf_file:
            writer = csv.DictWriter(csf_file, fieldnames=self._column_headings)

            writer.writeheader()

            for p in self._person_details:
                p_star = {key: value for key, value in p.items() if key in self._column_headings}

                writer.writerow(p_star)
        
        return result


    def _create_xlsx_file(self):
        result = DemographicsRequestXlsx(
            owner=self._user,
            last_updated_by_user=self._user,
            filename=self._filename,
            skip_pmi=self._skip_pmi,
        )

        db.session.add(result)
        db.session.commit()

        os.makedirs(os.path.dirname(result.filepath), exist_ok=True)

        wb = Workbook()
        ws = wb.active

        ws.append(self._column_headings)

        for p in self._person_details:
            p_star = []

            for h in self._column_headings:
                if h in p.keys():
                    p_star.append(p[h])
                else:
                    p_star.append('')
            ws.append(p_star)

        wb.save(filename=result.filepath)

        return result


    def _create_xls_file(self):
        result = DemographicsRequestExcel97(
            owner=self._user,
            last_updated_by_user=self._user,
            filename=self._filename,
            skip_pmi=self._skip_pmi,
        )

        db.session.add(result)
        db.session.commit()

        os.makedirs(os.path.dirname(result.filepath), exist_ok=True)

        wb = xlwt.Workbook()
        ws = wb.add_sheet('Test Sheet')
        style = xlwt.XFStyle()
        style.num_format_str = 'D-MMM-YY' # Other options: D-MMM-YY, D-MMM, MMM-YY, h:mm, h:mm:ss, h:mm, h:mm:ss, M/D/YY h:mm, mm:ss, [h]:mm:ss, mm:ss.0

        row_index = 0
        for col_index, h in enumerate(self._column_headings):
            ws.write(row_index, col_index, h)

        for row_index, p in enumerate(self._person_details, 1):
            for col_index, h in enumerate(self._column_headings):
                if h in p.keys():
                    ws.write(row_index, col_index, p[h], style)

        wb.save(result.filepath)

        return result
