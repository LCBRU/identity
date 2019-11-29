import re
import traceback
from datetime import datetime
from dateutil.parser import parse
from flask import url_for, current_app, render_template
from identity.database import db
from identity.celery import celery
from identity.demographics.model import (
    DemographicsRequest,
    DemographicsRequestData,
    DemographicsRequestDataMessage,
    DemographicsRequestDataResponse,
)
from identity.demographics.smsp import (
    get_demographics_from_search,
    get_demographics_from_nhs_number,
    SMSP_SEX_MALE,
    SMSP_SEX_FEMALE,
    SmspException,
)
from identity.utils import log_exception
from identity.emailing import email


def spine_lookup(demographics_request_data):
    error, v_nhs_number = convert_nhs_number(demographics_request_data.nhs_number)
    if error is not None:
        demographics_request_data.messages.append(
            DemographicsRequestDataMessage(
                type='warning',
                source='validation',
                scope='nhs_number',
                message=error,
            )
        )

    error, v_gender = convert_gender(demographics_request_data.gender)
    if error is not None:
        demographics_request_data.messages.append(
            DemographicsRequestDataMessage(
                type='warning',
                source='validation',
                scope='gender',
                message=error,
            )
        )
    elif not v_gender:
        demographics_request_data.messages.append(
            DemographicsRequestDataMessage(
                type='warning',
                source='validation',
                scope='gender',
                message='Missing value',
            )
        )

    error, v_family_name = convert_name(demographics_request_data.family_name)
    if error is not None:
        demographics_request_data.messages.append(
            DemographicsRequestDataMessage(
                type='warning',
                source='validation',
                scope='family_name',
                message=error,
            )
        )

    error, v_given_name = convert_name(demographics_request_data.given_name)
    if error is not None:
        demographics_request_data.messages.append(
            DemographicsRequestDataMessage(
                type='warning',
                source='validation',
                scope='given_name',
                message=error,
            )
        )

    error, v_dob = convert_dob(demographics_request_data.dob)
    if error is not None:
        demographics_request_data.messages.append(
            DemographicsRequestDataMessage(
                type='warning',
                source='validation',
                scope='dob',
                message=error,
            )
        )

    error, v_postcode = convert_postcode(demographics_request_data.postcode)
    if error is not None:
        demographics_request_data.messages.append(
            DemographicsRequestDataMessage(
                type='warning',
                source='validation',
                scope='postcode',
                message=error,
            )
        )

    try:
        if v_nhs_number and v_dob:
            demographics = get_demographics_from_nhs_number(
                nhs_number=v_nhs_number,
                dob=v_dob,
            )
        elif v_dob:
            demographics = get_demographics_from_search(
                family_name=v_family_name,
                given_name=v_given_name,
                gender=v_gender,
                dob=v_dob,
                postcode=v_postcode,
            )
        else:
            demographics_request_data.messages.append(
                DemographicsRequestDataMessage(
                    type='error',
                    source='validation',
                    scope='dob',
                    message='Missing required value',
                )
            )
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
        demographics_request_data.messages.append(
            DemographicsRequestDataMessage(
                type='error',
                source='spine',
                scope='request',
                message=e.message,
            )
        )
    except Exception as e:
        demographics_request_data.messages.append(
            DemographicsRequestDataMessage(
                type='unknown error',
                source='spine',
                scope='request',
                message=str(e),
            )
        )

    demographics_request_data.processed_datetime = datetime.utcnow()

    db.session.add(demographics_request_data)
    db.session.commit()


def convert_nhs_number(nhs_number):
    if not nhs_number:
        return None, ''

    # Nhs number is sometimes inputted xxx-xxx-xxxx, lets strip this down
    nhs_number = re.sub('[- ]', '', nhs_number)

    # A valid NHS number must be 10 digits long
    if not re.search(r'^[0-9]{10}$', nhs_number):
        return 'Invalid format', ''

    checkcalc = lambda sum: 11 - (sum % 11)

    char_total = sum(
        [int(j) * (11 - (i + 1)) for i, j in enumerate(nhs_number[:-1])]
    )
    checksum = checkcalc(char_total) if checkcalc(char_total) != 11 else 0

    if checksum != int(nhs_number[9]):
        return 'Invalid format', ''
    else:
        return None, nhs_number
    

def convert_gender(gender):
    gender = gender.lower()

    if not gender:
        return None, ''
    elif gender == 'f' or gender =='female':
        return None, SMSP_SEX_FEMALE
    elif gender == 'm' or gender == 'male':
        return None, SMSP_SEX_MALE
    else:
        return 'Invalid format', ''


def convert_name(name):
    if not name:
        return None, ''
    elif len(name) < 2:
        return 'Must be at least 2 characters', ''
    else:
        return None, name


def convert_dob(dob):
    if not dob:
        return None, ''

    dob_num = re.sub(r'[^0-9]', '', dob)

    if dob_num.isnumeric() and int(dob_num) > 19000101 and int(dob_num) < 21000101:
        return None, dob_num

    try:
        parsed_date = parse(dob, dayfirst=True)
    except ValueError:
        return 'Invalid date', ''

    if parsed_date.year < 1900 or parsed_date.year > datetime.utcnow().year:
        return 'Date out of range', ''
    else:
        return None, parsed_date.strftime("%Y%m%d")


def convert_postcode(postcode):
    if not postcode:
        return None, ''

    p = postcode.upper().replace(' ', '')
    p = "{} {}".format(p[0:-3], p[-3:])

    if not re.search(r'^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s[0-9][A-Za-z]{2})$', p):
        return 'Invalid format', ''
    else:
        return None, postcode


class ScheduleException(Exception):
    pass


def schedule_lookup_tasks(demographics_request_id):
    current_app.logger.info(f'schedule_lookup_tasks (demographics_request_id={demographics_request_id})')

    try:
        dr = DemographicsRequest.query.get(demographics_request_id)

        if dr is None:
            raise Exception('Request id={} not found'.format(demographics_request_id))

        if dr.paused:
            raise ScheduleException('Request id={} paused not running'.format(demographics_request_id))

        if dr.deleted:
            raise ScheduleException('Request id={} deleted'.format(demographics_request_id))

        if dr.result_created:
            raise ScheduleException('Request id={} result already created'.format(demographics_request_id))

        if dr.lookup_completed:
            current_app.logger.warning('Request id={} lookup already completed'.format(demographics_request_id))

        if not dr.data_extracted:
            extract_data.delay(dr.id)
        else:
            next_drd_id = db.session.query(DemographicsRequestData.id).filter(
                DemographicsRequestData.demographics_request_id == demographics_request_id
            ).filter(
                DemographicsRequestData.processed_datetime.is_(None)
            ).first()

            if next_drd_id is None:
                dr.lookup_completed_datetime = datetime.utcnow()
                db.session.add(dr)
                db.session.commit()

                produce_demographics_result.delay(demographics_request_id)
            else:
                next_drd_id, = next_drd_id
                process_demographics_request_data.delay(data_id=next_drd_id, request_id=demographics_request_id)

    except ScheduleException as sde:
        current_app.logger.warning(sde)
    except Exception as e:
        log_exception(e)
        save_demographics_error(demographics_request_id, e)


@celery.task()
def process_demographics_request_data(data_id, request_id):
    current_app.logger.info(f'process_demographics_request_data (data_id={data_id}, request_id={request_id})')

    try:
        drd = DemographicsRequestData.query.get(data_id)

        if drd is None:
            raise Exception('Data not found for ID = {}'.format(data_id))

        spine_lookup(drd)

        schedule_lookup_tasks(request_id)
    except Exception as e:
        log_exception(e)
        save_demographics_error(request_id, e)


@celery.task()
def extract_data(request_id):
    current_app.logger.info(f'extract_data (request_id={request_id})')

    try:
        current_app.logger.info('A')
        dr = DemographicsRequest.query.get(request_id)
        current_app.logger.info('B')

        if dr is None:
            current_app.logger.info('C')
            raise Exception('request not found')

        current_app.logger.info('D')
        cd = dr.column_definition

        current_app.logger.info('E')
        if len(dr.data) > 0:
            raise Exception(
                'Attempting to extract data from DemographicsRequest ("{}") '
                'that has already had data extracted.'.format(request_id)
            )

        current_app.logger.info('F')
        if cd is None:
            raise Exception(
                'Attempting to extract data from DemographicsRequest ("{}") '
                'that did not have a column definition.'.format(request_id)
            )

        current_app.logger.info('G')
        for i, r in enumerate(dr.iter_rows()):
            current_app.logger.info('H')
            nhs_number = (str(r[cd.nhs_number_column.name]) or '').strip() if cd.nhs_number_column is not None else None
            family_name = (str(r[cd.family_name_column.name]) or '').strip() if cd.family_name_column is not None else None
            given_name = (str(r[cd.given_name_column.name]) or '').strip() if cd.given_name_column is not None else None
            gender = (str(r[cd.gender_column.name]) or '').strip() if cd.gender_column is not None else None
            dob = (str(r[cd.dob_column.name]) or '').strip() if cd.dob_column is not None else None
            postcode = (str(r[cd.postcode_column.name]) or '').strip() if cd.postcode_column is not None else None

            d = DemographicsRequestData(
                demographics_request=dr,
                row_number=i,
                nhs_number=nhs_number,
                family_name=family_name,
                given_name=given_name,
                gender=gender,
                dob=dob,
                postcode=postcode,
            )

            dr.data.append(d)
        
        dr.data_extracted_datetime = datetime.utcnow()
        db.session.add(dr)
        db.session.commit()

        schedule_lookup_tasks(request_id)

    except Exception as e:
        current_app.logger.info('J')
        db.session.rollback()
        log_exception(e)
        save_demographics_error(request_id, e)


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


def save_demographics_error(demographics_request_id, e):
    dr = DemographicsRequest.query.get(demographics_request_id)
    if dr is not None:
        dr = DemographicsRequest.query.get(demographics_request_id)
        dr.set_error(traceback.format_exc())
        db.session.add(dr)
        db.session.commit()
