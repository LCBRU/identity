import re
import traceback
from datetime import datetime, date
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

    if demographics_request_data.pmi_data:
        error, v_pmi_nhs_number = convert_nhs_number(demographics_request_data.pmi_data.nhs_number)
        if error is not None:
            demographics_request_data.messages.append(
                DemographicsRequestDataMessage(
                    type='warning',
                    source='validation',
                    scope='pmi_nhs_number',
                    message=error,
                )
            )
    else:
        v_pmi_nhs_number = None

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

    if demographics_request_data.pmi_data:
        error, v_pmi_dob = convert_dob(demographics_request_data.pmi_data.date_of_birth)
        if error is not None:
            demographics_request_data.messages.append(
                DemographicsRequestDataMessage(
                    type='warning',
                    source='validation',
                    scope='pmi_date_of_birth',
                    message=error,
                )
            )
    else:
        v_pmi_dob = None

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
        # Use NHS Number and DOB from PMI, if not supplied
        v_nhs_number = v_nhs_number or v_pmi_nhs_number
        v_dob = v_dob or v_pmi_dob

        if v_nhs_number and v_dob:
            demographics = get_demographics_from_nhs_number(
                nhs_number=v_nhs_number,
                dob=v_dob,
            )
        elif v_dob:
            if not v_gender:
                demographics_request_data.messages.append(
                    DemographicsRequestDataMessage(
                        type='warning',
                        source='validation',
                        scope='gender',
                        message='Missing value',
                    )
                )

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
        return f'Invalid format {nhs_number}', ''

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
    if not gender:
        return None, ''

    gender = gender.lower()

    if gender == 'f' or gender =='female':
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
    current_app.logger.info(f'convert_dob (dob={dob})')

    if not dob:
        current_app.logger.info(f'convert_dob: DOB is empty')
        return None, ''

    if isinstance(dob, date) or isinstance(dob, datetime):
        current_app.logger.info(f'convert_dob: DOB is a date')
        return None, dob.strftime("%Y%m%d")


    ansi_match = re.fullmatch(r'(?P<year>\d{4})[\\ -]?(?P<month>\d{2})[\\ -]?(?P<day>\d{2})', dob)

    if ansi_match:
        return None, ansi_match.group('year') + ansi_match.group('month') + ansi_match.group('day')

    try:
        parsed_date = parse(dob, dayfirst=True)
    except ValueError:
        current_app.logger.info(f'convert_dob: DOB is something we don\'t understand')
        return 'Invalid date', ''

    if parsed_date.year < 1900 or parsed_date.year > datetime.utcnow().year:
        current_app.logger.info(f'convert_dob: DOB looks like a date, but it\'s out of range')
        return 'Date out of range', ''
    else:
        current_app.logger.info(f'convert_dob: DOB is a string that contains a date that we have successfully parsed.')
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

        next_drd_id = db.session.query(DemographicsRequestData.id).filter(
            DemographicsRequestData.demographics_request_id == demographics_request_id
        ).filter(
            DemographicsRequestData.processed_datetime.is_(None)
        ).first()

        if not dr.data_extracted:
            current_app.logger.info(f'Scheduling data extraction for demographics_request_id={demographics_request_id})')
            extract_data.delay(demographics_request_id)
        elif not dr.pmi_data_pre_completed:
            current_app.logger.info(f'Scheduling PMI download pre for demographics_request_id={demographics_request_id})')

            extract_pmi_details.delay(demographics_request_id)

            dr.pmi_data_pre_completed_datetime = datetime.utcnow()
            db.session.add(dr)
            db.session.commit()

        elif not dr.lookup_completed and next_drd_id is None:
            dr.lookup_completed_datetime = datetime.utcnow()
            db.session.add(dr)
            db.session.commit()

            schedule_lookup_tasks(demographics_request_id)

        elif not dr.lookup_completed and next_drd_id is not None:
            current_app.logger.info(f'Scheduling demographics download for demographics_request_id={demographics_request_id})')

            next_drd_id, = next_drd_id
            process_demographics_request_data.delay(data_id=next_drd_id, request_id=demographics_request_id)

        elif not dr.pmi_data_post_completed:
            current_app.logger.info(f'Scheduling PMI download post for demographics_request_id={demographics_request_id})')

            extract_pmi_details.delay(demographics_request_id)

            dr.pmi_data_post_completed_datetime = datetime.utcnow()
            db.session.add(dr)
            db.session.commit()

        elif not dr.result_created_datetime:
            current_app.logger.info(f'Scheduling result creation demographics_request_id={demographics_request_id})')

            produce_demographics_result.delay(demographics_request_id)


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
            schedule_lookup_tasks(request_id)
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
            uhl_system_number = (str(r[cd.uhl_system_number_column.name]) or '').strip() if cd.uhl_system_number_column is not None else None
            nhs_number = (str(r[cd.nhs_number_column.name]) or '').strip() if cd.nhs_number_column is not None else None
            family_name = (str(r[cd.family_name_column.name]) or '').strip() if cd.family_name_column is not None else None
            given_name = (str(r[cd.given_name_column.name]) or '').strip() if cd.given_name_column is not None else None
            gender = (str(r[cd.gender_column.name]) or '').strip() if cd.gender_column is not None else None
            dob = (str(r[cd.dob_column.name]) or '').strip() if cd.dob_column is not None else None
            postcode = (str(r[cd.postcode_column.name]) or '').strip() if cd.postcode_column is not None else None

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

            dr.data.append(d)

        dr.data_extracted_datetime = datetime.utcnow()
        db.session.add(dr)
        db.session.commit()

        schedule_lookup_tasks(request_id)

    except Exception as e:
        db.session.rollback()
        log_exception(e)
        save_demographics_error(request_id, e)


@celery.task()
def extract_pmi_details(request_id):
    current_app.logger.info(f'extract_pmi_details (request_id={request_id})')

    try:
        dr = DemographicsRequest.query.get(request_id)

        if dr is None:
            raise Exception('request not found')

        for d in dr.data:
            pmi_details = get_pmi_details(d.nhs_number, d.uhl_system_number)

            if pmi_details is not None:
                pmi_details.demographics_request_data_id = d.id
                db.session.add(pmi_details)

        db.session.commit()

        schedule_lookup_tasks(request_id)

    except Exception as e:
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


def get_pmi_details(*ids):
    result = None
    with pmi_engine() as conn:
        for id in ids:
            pmi_result = conn.execute(text("""
                SELECT
                    nhs_number,
                    main_pat_id as uhl_system_number,
                    last_name as family_name,
                    first_name as given_name,
                    gender,
                    dob,
                    date_of_death,
                    postcode
                FROM [dbo].[UHL_PMI_QUERY_BY_ID](:id)
                """), id=id)

            pmi_records = pmi_result.fetchall()

            if len(pmi_records) > 1:
                raise Exception(f"More than one participant found with id='{id}' in the UHL PMI")

            if len(pmi_records) == 1 and pmi_records[0]['uhl_system_number'] is not None:
                pmi_record = pmi_records[0]

                pmi_details = DemographicsRequestPmiData(
                    nhs_number=(pmi_record['nhs_number'] or '').replace(' ', ''),
                    uhl_system_number=pmi_record['uhl_system_number'],
                    family_name=pmi_record['family_name'],
                    given_name=pmi_record['given_name'],
                    gender=pmi_record['gender'],
                    date_of_birth=pmi_record['dob'],
                    date_of_death=pmi_record['date_of_death'],
                    postcode=pmi_record['postcode'],
                )
                if result is None:
                    result = pmi_details
                else:
                    if result != pmi_details:
                        raise Exception(f"Participant PMI mismatch for IDs '{ids}'")

        
    return result
