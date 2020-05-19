import traceback
from typing import NamedTuple
from collections import namedtuple
from datetime import datetime
from dateutil.parser import parse
from flask import url_for, current_app, render_template
from sqlalchemy.sql import text
from identity.database import db, pmi_engine
from identity.celery import celery
from identity.demographics.model import (
    DemographicsRequest,
    DemographicsRequestData,
    DemographicsRequestPmiData,
    DemographicsRequestDataMessage,
    DemographicsRequestDataResponse,
)
from identity.demographics.smsp import (
    get_demographics_from_search,
    get_demographics_from_nhs_number,
    SmspException,
)
from identity.utils import log_exception
from identity.emailing import email
from identity.services.pmi import get_pmi, PmiException
from .data_conversions import (
    convert_dob,
    convert_gender,
    convert_name,
    convert_nhs_number,
    convert_postcode,
    convert_uhl_system_number,
)


class ScheduleException(Exception):
    pass


def schedule_lookup_tasks(demographics_request_id):
    current_app.logger.info(f'schedule_lookup_tasks (demographics_request_id={demographics_request_id})')

    try:
        dr = DemographicsRequest.query.get(demographics_request_id)

        if dr is None:
            raise Exception('Request id={} not found'.format(demographics_request_id))

        if dr.paused or dr.deleted or dr.result_created or dr.in_error:
            raise ScheduleException(f'Request id={demographics_request_id} scheduled when status is "{dr.status}""')

        current_app.logger.info(f'Scheduling demographics_request_id={demographics_request_id} with status "{dr.status}"')

        if not dr.data_extracted:
            extract_data.delay(demographics_request_id)
        elif not dr.pmi_data_pre_completed:
            extract_pre_pmi_details.delay(demographics_request_id)
        elif not dr.lookup_completed:
            process_demographics_request_data.delay(demographics_request_id)
        elif not dr.pmi_data_post_completed:
            extract_post_pmi_details.delay(demographics_request_id)
        elif not dr.result_created_datetime:
            produce_demographics_result.delay(demographics_request_id)

        db.session.add(dr)
        db.session.commit()

    except ScheduleException as sde:
        current_app.logger.warning(sde)
    except Exception as e:
        log_exception(e)
        save_demographics_error(demographics_request_id, e)


class SpineParameters:

    Warning = namedtuple('Warning', ['scope', 'message', 'message_type', 'source'])

    def __init__(self):
        self.nhs_number = None
        self.family_name = None
        self.given_name = None
        self.gender = None
        self.dob = None
        self.postcode = None
        self.warnings = []

    @property
    def valid_nhs_number_lookup_parameters(self):
        return self.nhs_number and self.dob

    @property
    def valid_search_lookup_parameters(self):
        return self.dob and self.gender
    
    def add_warning(self, scope, message, message_type='warning', source='validation'):
        self.warnings.append(SpineParameters.Warning(scope=scope, message=message, message_type=message_type, source=source))


def spine_lookup(demographics_request_data):
    params = get_spine_parameters(demographics_request_data)

    try:
        if params.valid_nhs_number_lookup_parameters:
            demographics = get_demographics_from_nhs_number(
                nhs_number=params.nhs_number,
                dob=params.dob,
            )
        elif params.valid_search_lookup_parameters:
            if not params.gender:
                params.add_warning(scope='gender', message='Missing value')

            demographics = get_demographics_from_search(
                family_name=params.family_name,
                given_name=params.given_name,
                gender=params.gender,
                dob=params.dob,
                postcode=params.postcode,
            )
        else:
            params.add_warning(message_type='error', scope='request', message='Not enough values to perform Spine lookup')
            demographics = None

        if demographics:
            demographics_request_data.response = DemographicsRequestDataResponse(
                nhs_number=demographics.nhs_number,
                title=demographics.title,
                forename=demographics.forename,
                middlenames=demographics.middlenames,
                lastname=demographics.lastname,
                sex=demographics.sex,
                postcode=demographics.postcode,
                address=demographics.address,
                date_of_birth=parse(demographics.date_of_birth) if demographics.date_of_birth else None,
                date_of_death=parse(demographics.date_of_death) if demographics.date_of_death else None,
                is_deceased=demographics.is_deceased,
                current_gp_practice_code=demographics.current_gp_practice_code,
            )

    except SmspException as e:
        params.add_warning(message_type='error', source='spine', scope='request', message=e.message)
    except Exception as e:
        params.add_warning(message_type='unknown error', source='spine', scope='request', message=str(e))
    finally:
        for w in params.warnings:
            demographics_request_data.messages.append(
                DemographicsRequestDataMessage(
                    type=w.message_type,
                    source=w.source,
                    scope=w.scope,
                    message=w.message,
                )
            )


def get_spine_parameters(demographics_request_data):
    result = SpineParameters()

    error, v_nhs_number = convert_nhs_number(demographics_request_data.nhs_number)
    if error is not None:
        result.add_warning(scope='nhs_number', message=error)

    error, v_gender = convert_gender(demographics_request_data.gender)
    if error is not None:
        result.add_warning(scope='gender', message=error)

    error, v_family_name = convert_name(demographics_request_data.family_name)
    if error is not None:
        result.add_warning(scope='family_name', message=error)

    error, v_given_name = convert_name(demographics_request_data.given_name)
    if error is not None:
        result.add_warning(scope='given_name', message=error)

    error, v_dob = convert_dob(demographics_request_data.dob)
    if error is not None:
        result.add_warning(scope='dob', message=error)

    error, v_postcode = convert_postcode(demographics_request_data.postcode)
    if error is not None:
        result.add_warning(scope='postcode', message=error)

    if demographics_request_data.pmi_data:
        error, v_pmi_nhs_number = convert_nhs_number(demographics_request_data.pmi_data.nhs_number)
        if error is not None:
            result.add_warning(scope='pmi_nhs_number', message=error)

        error, v_pmi_gender = convert_gender(demographics_request_data.pmi_data.gender)
        if error is not None:
            result.add_warning(scope='pmi_gender', message=error)

        error, v_pmi_family_name = convert_name(demographics_request_data.pmi_data.family_name)
        if error is not None:
            result.add_warning(scope='pmi_family_name', message=error)

        error, v_pmi_given_name = convert_name(demographics_request_data.pmi_data.given_name)
        if error is not None:
            result.add_warning(scope='pmi_given_name', message=error)

        error, v_pmi_dob = convert_dob(demographics_request_data.pmi_data.date_of_birth)
        if error is not None:
            result.add_warning(scope='pmi_date_of_birth', message=error)

        error, v_pmi_postcode = convert_postcode(demographics_request_data.pmi_data.postcode)
        if error is not None:
            result.add_warning(scope='pmi_postcode', message=error)

    else:
        v_pmi_nhs_number = None
        v_pmi_gender = None
        v_pmi_family_name = None
        v_pmi_given_name = None
        v_pmi_dob = None
        v_pmi_postcode = None

    result.nhs_number=(v_nhs_number or v_pmi_nhs_number)
    result.dob=(v_dob or v_pmi_dob)
    result.family_name=(v_family_name or v_pmi_family_name)
    result.given_name=(v_given_name or v_pmi_given_name)
    result.gender=(v_gender or v_pmi_gender)
    result.postcode=(v_postcode or v_pmi_postcode)

    return result


@celery.task()
def process_demographics_request_data(request_id):
    current_app.logger.info(f'process_demographics_request_data: request_id={request_id})')

    try:
        dr = DemographicsRequest.query.get(request_id)

        if dr is None:
            raise Exception('request not found')

        drd = DemographicsRequestData.query.filter_by(demographics_request_id=request_id).filter(
            DemographicsRequestData.processed_datetime.is_(None)
        ).first()

        if drd is None:
            dr.lookup_completed_datetime = datetime.utcnow()
            db.session.add(dr)
        else:
            if not drd.has_error:
                spine_lookup(drd)
    
            drd.processed_datetime = datetime.utcnow()

            db.session.add(drd)

        db.session.commit()

        schedule_lookup_tasks(request_id)

    except Exception as e:
        log_exception(e)
        save_demographics_error(request_id, e)


@celery.task()
def extract_data(request_id):
    current_app.logger.info(f'extract_data (request_id={request_id})')

    try:
        dr = DemographicsRequest.query.get(request_id)

        if dr is None:
            raise Exception('request not found')

        cd = dr.column_definition

        if len(dr.data) > 0:
            raise Exception(
                'Attempting to extract data from DemographicsRequest ("{}") '
                'that has already had data extracted.'.format(request_id)
            )

        if cd is None:
            raise Exception(
                'Attempting to extract data from DemographicsRequest ("{}") '
                'that did not have a column definition.'.format(request_id)
            )

        for i, r in enumerate(dr.iter_rows()):
            uhl_system_number = get_column_value(r, cd.uhl_system_number_column)
            nhs_number = get_column_value(r, cd.nhs_number_column)
            family_name = get_column_value(r, cd.family_name_column)
            given_name = get_column_value(r, cd.given_name_column)
            gender = get_column_value(r, cd.gender_column)
            dob = get_column_value(r, cd.dob_column)
            postcode = get_column_value(r, cd.postcode_column)

            if any([uhl_system_number, nhs_number, family_name, given_name, gender, dob, postcode]):
                d = DemographicsRequestData(
                    demographics_request=dr,
                    row_number=i,
                    uhl_system_number=uhl_system_number,
                    nhs_number=nhs_number,
                    family_name=family_name,
                    given_name=given_name,
                    gender=gender,
                    dob=dob,
                    postcode=postcode,
                )

                current_app.logger.info(f'Saving extracting data={d}')

                dr.data.append(d)
            else:
                current_app.logger.info(f'Skipping empty data')

        dr.data_extracted_datetime = datetime.utcnow()
        db.session.add(dr)
        db.session.commit()

        schedule_lookup_tasks(request_id)

    except Exception as e:
        db.session.rollback()
        log_exception(e)
        save_demographics_error(request_id, e)


def get_column_value(record, column):
    if column is None:
        return ''

    if record[column.name] is None:
        return ''
    else:
        return str(record[column.name]).strip()


@celery.task()
def produce_demographics_result(demographics_request_id):
    current_app.logger.info(f'produce_demographics_result (demographics_request_id={demographics_request_id})')

    try:
        dr = DemographicsRequest.query.get(demographics_request_id)

        dr.create_result()

        dr.result_created_datetime = datetime.utcnow()

        db.session.add(dr)

        email(
            subject='Identity Demographics Request Complete',
            recipients=[dr.owner.email],
            message='Your demographics request {} is complete.'.format(
                url_for('ui.demographics', _external=True),
            ),
            html=render_template('email/request_complete.html', request=dr),
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log_exception(e)
        save_demographics_error(demographics_request_id, e)


@celery.task()
def extract_pre_pmi_details(request_id):
    current_app.logger.info(f'extract_pre_pmi_details (request_id={request_id})')

    extract_pmi_details(
        request_id=request_id,
        data_selection_condition=DemographicsRequestData.pmi_pre_processed_datetime.is_(None),
        request_completed_attribute='pmi_data_pre_completed_datetime',
        data_completed_attribute='pmi_pre_processed_datetime',
    )


@celery.task()
def extract_post_pmi_details(request_id):
    current_app.logger.info(f'extract_pre_pmi_details (request_id={request_id})')

    extract_pmi_details(
        request_id=request_id,
        data_selection_condition=DemographicsRequestData.pmi_post_processed_datetime.is_(None),
        request_completed_attribute='pmi_data_post_completed_datetime',
        data_completed_attribute='pmi_post_processed_datetime',
    )


def extract_pmi_details(request_id, data_selection_condition, request_completed_attribute, data_completed_attribute):
    current_app.logger.info(f'extract_pmi_details (request_id={request_id})')

    try:
        dr = DemographicsRequest.query.get(request_id)

        if dr is None:
            raise Exception('request not found')

        drd = DemographicsRequestData.query.filter_by(demographics_request_id=request_id).filter(data_selection_condition).first()

        if drd is None:
            current_app.logger.info(f'extract_pmi_details (request_id={request_id}): Done')
            setattr(dr, request_completed_attribute, datetime.utcnow())
            db.session.add(dr)
        else:
            if not drd.has_error and drd.pmi_data is None:
                get_pmi_details(drd)

            setattr(drd, data_completed_attribute, datetime.utcnow())
            db.session.add(drd)

        db.session.commit()

        schedule_lookup_tasks(request_id)

    except Exception as e:
        db.session.rollback()
        log_exception(e)
        save_demographics_error(request_id, e)


def get_pmi_details(drd):
    current_app.logger.info(f'get_pmi_details (Data request Data={drd.id})')

    try:
        error, v_nhs_number = convert_nhs_number(drd.nhs_number)
        if error is not None:
            drd.messages.append(
                DemographicsRequestDataMessage(
                    type='warning',
                    source='pmi_details',
                    scope='nhs_number',
                    message=error,
                )
            )

        error, v_s_number = convert_uhl_system_number(drd.uhl_system_number)
        if error is not None:
            drd.messages.append(
                DemographicsRequestDataMessage(
                    type='warning',
                    source='pmi_details',
                    scope='uhl_system_number',
                    message=error,
                )
            )

        pmi = get_pmi(nhs_number=v_nhs_number, uhl_system_number=v_s_number)

        if pmi is not None:
            pmi_details = DemographicsRequestPmiData(**pmi._asdict())

            pmi_details.demographics_request_data_id = drd.id
            db.session.add(pmi_details)

    except PmiException as e:
        drd.messages.append(
            DemographicsRequestDataMessage(
                type='error',
                source='pmi_details',
                scope='pmi_details',
                message=e.message,
            ))
    except Exception as e:
        log_exception(e)
        drd.messages.append(
            DemographicsRequestDataMessage(
                type='error',
                source='pmi_details',
                scope='pmi_details',
                message=traceback.format_exc(),
            ))


def save_demographics_error(demographics_request_id, e):
    dr = DemographicsRequest.query.get(demographics_request_id)
    if dr is not None:
        dr = DemographicsRequest.query.get(demographics_request_id)
        dr.set_error(traceback.format_exc())
        db.session.add(dr)
        db.session.commit()
