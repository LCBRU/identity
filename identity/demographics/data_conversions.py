import re
from datetime import datetime, date
from flask import current_app
from identity.demographics.smsp import (
    SMSP_SEX_MALE,
    SMSP_SEX_FEMALE,
)
from identity.validators import (
    is_invalid_nhs_number,
    standardise_nhs_number,
    is_invalid_uhl_system_number,
    parse_date,
    is_invalid_dob,
    standardise_postcode,
    is_invalid_postcode,
)


def convert_nhs_number(nhs_number):
    current_app.logger.info(f'convert_nhs_number (nhs_number={nhs_number})')

    if not nhs_number:
        return None, ''

    nhs_number = standardise_nhs_number(nhs_number)

    if is_invalid_nhs_number(nhs_number):
        return f'Invalid format {nhs_number}', ''

    return None, nhs_number
    

def convert_uhl_system_number(uhl_system_number):
    current_app.logger.info(f'convert_uhl_system_number (uhl_system_number={uhl_system_number})')

    uhl_system_number = (uhl_system_number or '').strip()

    if not uhl_system_number:
        return None, ''

    if is_invalid_uhl_system_number(uhl_system_number):
        return f'Invalid format {uhl_system_number}', ''

    return None, uhl_system_number
    

def convert_gender(gender):
    current_app.logger.info(f'convert_gender (gender={gender})')

    gender = (gender or '').strip()

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
    current_app.logger.info(f'convert_name (name={name})')

    name = (name or '').strip()

    if not name:
        return None, ''
    elif len(name) < 2:
        return 'Must be at least 2 characters', ''
    else:
        return None, name


def convert_dob(dob):
    current_app.logger.info(f'convert_dob (dob={dob})')

    try:
        parsed_dob = parse_date(dob)
    except ValueError:
        return 'Invalid date', ''

    if is_invalid_dob(parsed_dob):
        return 'Date out of range', ''
    else:
        return None, parsed_dob.strftime("%Y%m%d")


def convert_postcode(postcode):
    current_app.logger.info(f'convert_postcode (postcode={postcode})')

    postcode = standardise_postcode(postcode or '')

    if not is_invalid_postcode(postcode):
        return None, postcode
    else:
        return 'Invalid format', ''
