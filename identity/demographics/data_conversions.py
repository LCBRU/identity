import re
from datetime import datetime, date
from dateutil.parser import parse
from flask import current_app
from identity.demographics.smsp import (
    SMSP_SEX_MALE,
    SMSP_SEX_FEMALE,
)


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
    

def convert_uhl_system_number(uhl_system_number):
    if not uhl_system_number:
        return None, ''

    if not re.search(r'^([SRFG]\d{7}|[U]\d{7}.*|LB\d{7}|RTD[\-0-9])$', uhl_system_number):
        return f'Invalid format {uhl_system_number}', ''
    else:
        return None, uhl_system_number
    

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


    ansi_match = re.fullmatch(r'(?P<year>\d{4})[\\ -]?(?P<month>\d{2})[\\ -]?(?P<day>\d{2})(?:[ T]\d{2}:\d{2}:\d{2})?(?:\.\d+)?(?:[+-]\d{2}:\d{2})?', dob)

    if ansi_match:
        current_app.logger.info(f'convert_dob: DOB is an ANSI date string')
        return None, ansi_match.group('year') + ansi_match.group('month') + ansi_match.group('day')

    try:
        parsed_date = parse(dob, dayfirst=True)
    except ValueError:
        current_app.logger.error(f'convert_dob: DOB is something we don\'t understand: {dob}')
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
