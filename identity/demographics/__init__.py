import traceback
from datetime import datetime, UTC
from flask import url_for, current_app, render_template
from lbrc_flask.database import db
from identity.celery import celery
from identity.demographics.model import (
    DemographicsRequest,
    DemographicsRequestData,
    DemographicsRequestPmiData,
    DemographicsRequestDataMessage,
)
from lbrc_flask.logging import log_exception
from lbrc_flask.emailing import email
from identity.services.pmi import get_pmi, PmiException
from lbrc_flask.data_conversions import convert_nhs_number, convert_uhl_system_number
from sqlalchemy import select


class ScheduleException(Exception):
    pass


def schedule_lookup_tasks(demographics_request_id):
    do_lookup_tasks.delay(demographics_request_id)


@celery.task()
def do_lookup_tasks(demographics_request_id):
    current_app.logger.info(f'schedule_lookup_tasks (demographics_request_id={demographics_request_id})')

    try:
        dr = db.session.get(DemographicsRequest, demographics_request_id)

        if dr is None:
            raise Exception('Request id={} not found'.format(demographics_request_id))

        if dr.paused or dr.deleted or dr.result_created or dr.in_error:
            raise ScheduleException(f'Request id={demographics_request_id} scheduled when status is "{dr.status}""')

        current_app.logger.info(f'Scheduling demographics_request_id={demographics_request_id} with status "{dr.status}"')

        if not dr.data_extracted:
            extract_data.delay(demographics_request_id)
        elif not dr.pmi_data_pre_completed:
            extract_pre_pmi_details.delay(demographics_request_id)
        elif not dr.result_created_datetime:
            produce_demographics_result.delay(demographics_request_id)

        db.session.add(dr)
        db.session.commit()

    except ScheduleException as sde:
        current_app.logger.warning(sde)
    except Exception as e:
        log_exception(e)
        save_demographics_error(demographics_request_id, e)


@celery.task()
def extract_data(request_id):
    current_app.logger.info(f'extract_data (request_id={request_id})')

    try:
        dr = db.session.get(DemographicsRequest, request_id)

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

        dr.data_extracted_datetime = datetime.now(UTC)
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
        dr = db.session.get(DemographicsRequest, demographics_request_id)

        current_app.logger.info(f'produce_demographics_result: Creating result')
        dr.create_result()

        dr.result_created_datetime = datetime.now(UTC)

        db.session.add(dr)
        db.session.commit()

    except Exception as e:
        current_app.logger.info('produce_demographics_result: Rolling Back')
        db.session.rollback()
        log_exception(e)
        save_demographics_error(demographics_request_id, e)

    try:
        email(
            subject='Identity Demographics Request Complete',
            recipients=[dr.owner.email],
            message='Your demographics request {} is complete.'.format(
                url_for('ui.demographics', _external=True),
            ),
            html=render_template('email/request_complete.html', request=dr),
        )
    except Exception as e:
        current_app.logger.info('produce_demographics_result: Failed to send email, but everything else worked!')
        log_exception(e)


@celery.task()
def extract_pre_pmi_details(request_id):
    current_app.logger.info(f'extract_pre_pmi_details (request_id={request_id})')

    extract_pmi_details(
        request_id=request_id,
        data_selection_condition=DemographicsRequestData.pmi_pre_processed_datetime.is_(None),
        request_completed_attribute='pmi_data_pre_completed_datetime',
        data_completed_attribute='pmi_pre_processed_datetime',
    )


def extract_pmi_details(request_id, data_selection_condition, request_completed_attribute, data_completed_attribute):
    current_app.logger.info(f'extract_pmi_details (request_id={request_id})')

    try:
        dr = db.session.get(DemographicsRequest, request_id)

        if dr is None:
            raise Exception('request not found')

        q = (
            select(DemographicsRequestData)
            .where(DemographicsRequestData.demographics_request_id == request_id)
            .where(data_selection_condition)
        )
        drd = db.session.execute(q).scalars().first()

        if drd is None:
            current_app.logger.info(f'extract_pmi_details (request_id={request_id}): Done')
            setattr(dr, request_completed_attribute, datetime.now(UTC))
            db.session.add(dr)
        else:
            if not drd.has_error and drd.pmi_data is None:
                get_pmi_details(drd)

            setattr(drd, data_completed_attribute, datetime.now(UTC))
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
            dets = pmi._asdict()
            del dets['mapping']
            pmi_details = DemographicsRequestPmiData(**dets)

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
    dr = db.session.get(DemographicsRequest, demographics_request_id)
    if dr is not None:
        dr = db.session.get(DemographicsRequest, demographics_request_id)
        dr.set_error(traceback.format_exc())
        db.session.add(dr)
        db.session.commit()
