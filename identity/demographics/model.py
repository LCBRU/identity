import os
import csv
import re
import chardet
from shutil import copyfile
from itertools import takewhile
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from openpyxl import load_workbook
from flask import current_app
from datetime import datetime
from werkzeug.utils import secure_filename
from ..database import db
from ..model import User


class DemographicsRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    filename = db.Column(db.String(500))
    extension = db.Column(db.String(100), nullable=False)
    owner_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    owner = db.relationship(User, foreign_keys=[owner_user_id], backref=db.backref("demographic_requests"))
    submitted_datetime = db.Column(db.DateTime)
    deleted_datetime = db.Column(db.DateTime)
    paused_datetime = db.Column(db.DateTime)
    data_extracted_datetime = db.Column(db.DateTime)
    pmi_data_pre_completed_datetime =  db.Column(db.DateTime)
    pmi_data_post_completed_datetime =  db.Column(db.DateTime)
    lookup_completed_datetime = db.Column(db.DateTime)
    result_created_datetime = db.Column(db.DateTime)
    result_downloaded_datetime = db.Column(db.DateTime)
    error_datetime = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User, foreign_keys=[last_updated_by_user_id])
    column_definition = db.relationship("DemographicsRequestColumnDefinition", uselist=False, back_populates="demographics_request")

    __mapper_args__ = {
        "polymorphic_on": extension,
    }

    @property
    def filepath(self):
        return os.path.join(
            current_app.config["FILE_UPLOAD_DIRECTORY"],
            secure_filename(
                "{}_{}".format(self.last_updated_by_user.id, self.last_updated_by_user.full_name)
            ),
            secure_filename(
                "{}_{}".format(self.id, self.filename)
            ),
        )

    @property
    def result_filename(self):
        return secure_filename(
                "{}_result_{}".format(self.id, self.filename)
            )

    @property
    def result_filepath(self):
        return os.path.join(
            current_app.config["FILE_UPLOAD_DIRECTORY"],
            secure_filename(
                "{}_{}".format(self.last_updated_by_user.id, self.last_updated_by_user.full_name)
            ),
            self.result_filename,
        )

    def __lt__(self, other):
        return self.created_datetime < other.created_datetime

    @property
    def data_extracted(self):
        return self.data_extracted_datetime is not None

    @property
    def paused(self):
        return self.paused_datetime is not None

    @property
    def columns_defined(self):
        return self.column_definition and self.column_definition.is_valid

    @property
    def awaiting_submission(self):
        return self.columns_defined and self.submitted_datetime is None

    @property
    def submitted(self):
        return self.submitted_datetime is not None

    @property
    def deleted(self):
        return self.deleted_datetime is not None

    @property
    def result_created(self):
        return self.result_created_datetime is not None

    @property
    def pmi_data_pre_completed(self):
        return self.pmi_data_pre_completed_datetime is not None

    @property
    def pmi_data_post_completed(self):
        return self.pmi_data_post_completed_datetime is not None

    @property
    def result_downloaded(self):
        return self.result_downloaded_datetime is not None

    @property
    def lookup_completed(self):
        return self.lookup_completed_datetime is not None

    @property
    def in_error(self):
        return self.error_datetime is not None

    @property
    def requires_column_definition(self):
        return not self.deleted and not self.submitted and not self.in_error
    
    @property
    def requires_submission(self):
        return not self.deleted and self.awaiting_submission and not self.in_error
    
    @property
    def can_be_resubmitted(self):
        return not self.deleted and self.submitted and not self.result_created and not self.in_error
    
    @property
    def can_be_paused(self):
        return not self.deleted and self.submitted and not self.result_created and not self.paused and not self.in_error
    
    @property
    def can_be_downloaded(self):
        return not self.deleted and self.result_created and not self.in_error
    
    @property
    def can_be_deleted(self):
        return not self.deleted

    @property
    def status(self):
        if self.deleted:
            return 'Deleted'
        elif self.in_error:
            return 'Error'
        elif self.paused:
            return 'Paused'
        if not self.columns_defined:
            return 'Uploaded'
        elif not self.submitted:
            return 'Awaiting Submission'
        elif not self.data_extracted:
            return 'Extracting Data'
        elif not self.lookup_completed:
            return 'Fetching Demographics {} of {}'.format(self.fetched_count, self.data_count)
        elif not self.result_created:
            return 'Processing Demographics'
        elif not self.result_downloaded:
            return 'Ready to Download'
        else:
            return 'Downloaded'

    @hybrid_property
    def data_count(self):
        return len(self.data)

    @data_count.expression
    def data_count(cls):
        return (select([func.count(DemographicsRequestData.id)]).
                where(DemographicsRequestData.demographics_request_id == cls.id).
                label("data_count")
                )

    @hybrid_property
    def fetched_count(self):
        return len([d for d in self.data if d.processed])

    @fetched_count.expression
    def fetched_count(cls):
        return (select([func.count(DemographicsRequestData.id)]).
                where(DemographicsRequestData.demographics_request_id == cls.id).
                where(DemographicsRequestData.processed_datetime.isnot(None)).
                label("fetched_count")
                )

    def get_most_likely_nhs_number_column_id(self):
        return self._get_most_likely_column_id('nhs.*(number|no)')

    def get_most_likely_family_name_column_id(self):
        return self._get_most_likely_column_id('(surname|family.*name)')

    def get_most_likely_given_name_column_id(self):
        return self._get_most_likely_column_id('(first|given|fore).*name')

    def get_most_likely_gender_column_id(self):
        return self._get_most_likely_column_id('(gender|sex)')

    def get_most_likely_dob_column_id(self):
        return self._get_most_likely_column_id('(dob|date.*birth|birth.*date)')

    def get_most_likely_postcode_column_id(self):
        return self._get_most_likely_column_id('(post.*code)')

    def _get_most_likely_column_id(self, regular_expression):
        repat = re.compile(regular_expression, re.IGNORECASE)
        ids = (c.id for c in self.columns if re.search(repat, c.name))
        return next(ids, 0)

    def set_error(self, message):
        self.error_datetime = datetime.utcnow()
        self.error_message = message


class DemographicsRequestXslx(DemographicsRequest):
    __mapper_args__ = {
        "polymorphic_identity": '.xslx',
    }

    def get_column_names(self):
        wb = load_workbook(filename=self.filepath)
        ws = wb.active
        rows = ws.iter_rows(min_row=1, max_row=1)
        first_row = next(rows)

        return [c.value for c in takewhile(lambda x: x.value, first_row)]

    def iter_rows(self):
        wb = load_workbook(filename=self.filepath)
        ws = wb.active

        for r in ws.iter_rows(min_row=2, values_only=True):
            yield dict(zip(self.get_column_names(), r))

    def iter_result_rows(self):
        wb = load_workbook(filename=self.result_filepath)
        ws = wb.active

        rows = ws.iter_rows(min_row=1, max_row=1)
        first_row = next(rows)

        column_names = [c.value for c in takewhile(lambda x: x.value, first_row)]

        for r in ws.iter_rows(min_row=2, values_only=True):
            yield dict(zip(column_names, r))

    def create_result(self):
        current_app.logger.info('DemographicsRequestXslx.create_result')
        copyfile(self.filepath, self.result_filepath)

        wb = load_workbook(filename=self.result_filepath)
        ws = wb.active

        indexed_data = {d.row_number:d for d in self.data}
        insert_col = len(self.get_column_names()) + 1

        fieldnames = [
            'spine_nhs_number',
            'spine_title',
            'spine_forename',
            'spine_middlenames',
            'spine_lastname',
            'spine_sex',
            'spine_postcode',
            'spine_address',
            'spine_date_of_birth',
            'spine_date_of_death',
            'spine_is_deceased',
            'spine_current_gp_practice_code',
            'pmi_nhs_number',
            'pmi_uhl_system_number',
            'pmi_family_name',
            'pmi_given_name',
            'pmi_gender',
            'pmi_dob',
            'pmi_postcode',
            'spine_message',
        ]

        for i, fn in enumerate(fieldnames[::-1]):
            ws.insert_cols(insert_col)
            ws.cell(row=1, column=insert_col).value = fn

        for i, row in enumerate(self.iter_result_rows()):
            current_app.logger.info('row')
            if indexed_data[i].response:
                current_app.logger.info('response')
                ws.cell(row=i + 2, column=insert_col).value = indexed_data[i].response.nhs_number
                ws.cell(row=i + 2, column=insert_col + 1).value = indexed_data[i].response.title
                ws.cell(row=i + 2, column=insert_col + 2).value = indexed_data[i].response.forename
                ws.cell(row=i + 2, column=insert_col + 3).value = indexed_data[i].response.middlenames
                ws.cell(row=i + 2, column=insert_col + 4).value = indexed_data[i].response.lastname
                ws.cell(row=i + 2, column=insert_col + 5).value = indexed_data[i].response.sex
                ws.cell(row=i + 2, column=insert_col + 6).value = indexed_data[i].response.postcode
                ws.cell(row=i + 2, column=insert_col + 7).value = indexed_data[i].response.address
                if indexed_data[i].response.date_of_birth:
                    ws.cell(row=i + 2, column=insert_col + 8).value = indexed_data[i].response.date_of_birth.strftime('%d-%b-%Y')
                else:
                    ws.cell(row=i + 2, column=insert_col + 8).value = ''
                if indexed_data[i].response.date_of_death:
                    ws.cell(row=i + 2, column=insert_col + 9).value = indexed_data[i].response.date_of_death.strftime('%d-%b-%Y')
                else:
                    ws.cell(row=i + 2, column=insert_col + 9).value = ''
                ws.cell(row=i + 2, column=insert_col + 10).value = 'True' if indexed_data[i].response.is_deceased else 'False'
                ws.cell(row=i + 2, column=insert_col + 11).value = indexed_data[i].response.current_gp_practice_code

                pmi_data = indexed_data[i].pmi_data
                if pmi_data is not None:
                    current_app.logger.info('pmi_data')
                    ws.cell(row=i + 2, column=insert_col + 12).value = pmi_data.nhs_number
                    ws.cell(row=i + 2, column=insert_col + 13).value = pmi_data.uhl_system_number
                    ws.cell(row=i + 2, column=insert_col + 14).value = pmi_data.family_name
                    ws.cell(row=i + 2, column=insert_col + 15).value = pmi_data.given_name
                    ws.cell(row=i + 2, column=insert_col + 16).value = pmi_data.gender
                    ws.cell(row=i + 2, column=insert_col + 17).value = pmi_data.date_of_birth
                    ws.cell(row=i + 2, column=insert_col + 18).value = pmi_data.postcode

            ws.cell(row=i + 2, column=insert_col + 19).value = '; '.join(['{} {} in {}: {}'.format(m.source, m.type, m.scope, m.message) for m in indexed_data[i].messages])


        wb.save(filename=self.result_filepath)


class DemographicsRequestCsv(DemographicsRequest):
    __mapper_args__ = {
        "polymorphic_identity": '.csv',
    }

    def get_column_names(self):
        with open(self.filepath, 'r', encoding=self._get_encoding()) as f:
            d_reader = csv.DictReader(f)

            return d_reader.fieldnames

    def _get_encoding(self):
        rawdata = open(self.filepath, 'rb').read()
        result = chardet.detect(rawdata)
        return result['encoding']

    def iter_rows(self):
        with open(self.filepath, 'r', encoding=self._get_encoding()) as f:
            reader = csv.DictReader(f)

            for row in reader:
                yield row

    def iter_result_rows(self):
        with open(self.result_filepath, 'r', encoding=self._get_encoding()) as f:
            reader = csv.DictReader(f)

            for row in reader:
                yield row

    def create_result(self):
        current_app.logger.info('DemographicsRequestCsv.create_result')
        with open(self.result_filepath, 'w', encoding=self._get_encoding()) as result_file:

            fieldnames = self.get_column_names()
            fieldnames.extend([
                'spine_nhs_number',
                'spine_title',
                'spine_forename',
                'spine_middlenames',
                'spine_lastname',
                'spine_sex',
                'spine_postcode',
                'spine_address',
                'spine_date_of_birth',
                'spine_date_of_death',
                'spine_is_deceased',
                'spine_current_gp_practice_code',
                'pmi_nhs_number',
                'pmi_uhl_system_number',
                'pmi_family_name',
                'pmi_given_name',
                'pmi_gender',
                'pmi_dob',
                'pmi_postcode',
                'spine_message',
            ])

            writer = csv.DictWriter(result_file, fieldnames=fieldnames)
            writer.writeheader()

            indexed_data = {d.row_number:d for d in self.data}

            for i, row in enumerate(self.iter_rows()):
                current_app.logger.info('row')

                response = indexed_data[i].response

                if response:
                    current_app.logger.info('response')
                    row['spine_nhs_number'] = response.nhs_number
                    row['spine_title'] = response.title
                    row['spine_forename'] = response.forename
                    row['spine_middlenames'] = response.middlenames
                    row['spine_lastname'] = response.lastname
                    row['spine_sex'] = response.sex
                    row['spine_postcode'] = response.postcode
                    row['spine_address'] = response.address
                    if response.date_of_birth:
                        row['spine_date_of_birth'] = response.date_of_birth.strftime('%d-%b-%Y')
                    if response.date_of_death:
                        row['spine_date_of_death'] = response.date_of_death.strftime('%d-%b-%Y')
                    row['spine_is_deceased'] = 'True' if response.is_deceased else 'False'
                    row['spine_current_gp_practice_code'] = response.current_gp_practice_code

                pmi_data = indexed_data[i].pmi_data
                if pmi_data is not None:
                    current_app.logger.info('pmi_data')
                    row['pmi_nhs_number'] = pmi_data.nhs_number
                    row['pmi_uhl_system_number'] = pmi_data.uhl_system_number
                    row['pmi_family_name'] = pmi_data.family_name
                    row['pmi_given_name'] = pmi_data.given_name
                    row['pmi_gender'] = pmi_data.gender
                    row['pmi_dob'] = pmi_data.date_of_birth
                    row['pmi_postcode'] = pmi_data.postcode

                row['spine_message'] = '; '.join(['{} {} in {}: {}'.format(m.source, m.type, m.scope, m.message) for m in indexed_data[i].messages])

                writer.writerow(row)


class DemographicsRequestColumn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    demographics_request_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequest.id))
    demographics_request = db.relationship(DemographicsRequest, foreign_keys=[demographics_request_id], backref=db.backref("columns"))
    name = db.Column(db.String(500))
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User, foreign_keys=[last_updated_by_user_id])

    def __lt__(self, other):
        return self.name < other.name


class DemographicsRequestColumnDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    demographics_request_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequest.id))
    demographics_request = db.relationship(DemographicsRequest, foreign_keys=[demographics_request_id], back_populates="column_definition")
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User, foreign_keys=[last_updated_by_user_id])

    nhs_number_column_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequestColumn.id))
    nhs_number_column = db.relationship(DemographicsRequestColumn, foreign_keys=[nhs_number_column_id])
    family_name_column_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequestColumn.id))
    family_name_column = db.relationship(DemographicsRequestColumn, foreign_keys=[family_name_column_id])
    given_name_column_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequestColumn.id))
    given_name_column = db.relationship(DemographicsRequestColumn, foreign_keys=[given_name_column_id])
    gender_column_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequestColumn.id))
    gender_column = db.relationship(DemographicsRequestColumn, foreign_keys=[gender_column_id])
    dob_column_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequestColumn.id))
    dob_column = db.relationship(DemographicsRequestColumn, foreign_keys=[dob_column_id])
    postcode_column_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequestColumn.id))
    postcode_column = db.relationship(DemographicsRequestColumn, foreign_keys=[postcode_column_id])

    @property
    def is_valid(self):
        return (
            self.nhs_number_column_id is not None
            and self.dob_column_id is not None
        ) or (
            self.family_name_column_id is not None
            and self.given_name_column_id is not None
            and self.dob_column_id is not None
            and self.gender_column_id is not None
            and self.postcode_column_id is not None
        )


class DemographicsRequestData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    demographics_request_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequest.id))
    row_number = db.Column(db.Integer, nullable=False)
    demographics_request = db.relationship(DemographicsRequest, backref=db.backref("data"))
    response = db.relationship("DemographicsRequestDataResponse", uselist=False, back_populates="demographics_request_data")
    pmi_data = db.relationship("DemographicsRequestPmiData", uselist=False, back_populates="demographics_request_data")

    nhs_number = db.Column(db.String)
    uhl_system_number = db.Column(db.String)
    family_name = db.Column(db.String)
    given_name = db.Column(db.String)
    gender = db.Column(db.String)
    dob = db.Column(db.String)
    postcode = db.Column(db.String)

    created_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    processed_datetime = db.Column(db.DateTime)

    @property
    def processed(self):
        return self.processed_datetime is not None



class DemographicsRequestPmiData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    demographics_request_data_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequestData.id))
    demographics_request_data = db.relationship(DemographicsRequestData, foreign_keys=[demographics_request_data_id], back_populates="pmi_data")

    nhs_number = db.Column(db.String)
    uhl_system_number = db.Column(db.String)
    family_name = db.Column(db.String)
    given_name = db.Column(db.String)
    gender = db.Column(db.String)
    date_of_birth = db.Column(db.Date)
    date_of_death = db.Column(db.Date)
    postcode = db.Column(db.String)

    created_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __eq__(self, other):
        if isinstance(other, DemographicsRequestPmiData):
            return (
                self.nhs_number == other.nhs_number and
                self.uhl_system_number == other.uhl_system_number and
                self.family_name == other.family_name and
                self.given_name == other.given_name and
                self.gender == other.gender and
                self.date_of_birth == other.date_of_birth and
                self.date_of_death == other.date_of_death and
                self.postcode == other.postcode
            )
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class DemographicsRequestDataMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    demographics_request_data_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequestData.id))
    demographics_request_data = db.relationship(DemographicsRequestData, backref=db.backref("messages"))

    type = db.Column(db.String)
    source = db.Column(db.String)
    scope = db.Column(db.String)
    message = db.Column(db.String)
    created_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class DemographicsRequestDataResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    demographics_request_data_id = db.Column(db.Integer, db.ForeignKey(DemographicsRequestData.id))
    demographics_request_data = db.relationship(DemographicsRequestData, foreign_keys=[demographics_request_data_id], back_populates="response")
    created_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    nhs_number = db.Column(db.String)
    title = db.Column(db.String)
    forename = db.Column(db.String)
    middlenames = db.Column(db.String)
    lastname = db.Column(db.String)
    sex = db.Column(db.String)
    postcode = db.Column(db.String)
    address = db.Column(db.String)
    date_of_birth = db.Column(db.Date)
    date_of_death = db.Column(db.Date)
    is_deceased = db.Column(db.Boolean)
    current_gp_practice_code = db.Column(db.String)
