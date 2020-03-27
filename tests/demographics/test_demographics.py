# -*- coding: utf-8 -*-

import os
import pytest
import shutil
import datetime
from dateutil.parser import parse
from unittest.mock import patch, MagicMock, PropertyMock
from flask import current_app
from identity.database import db
from identity.demographics import (
    extract_data,
    spine_lookup,
    process_demographics_request_data,
    produce_demographics_result,
    get_pmi_details,
    extract_pre_pmi_details,
)
from identity.demographics.model import (
    DemographicsRequest,
    DemographicsRequestData,
    DemographicsRequestPmiData,
    DemographicsRequestDataMessage,
)
from identity.demographics.smsp import (
    SMSP_SEX_FEMALE,
    SMSP_SEX_MALE,
    SmspNoMatchException,
    SmspMultipleMatchesException,
    SmspNhsNumberSupersededException,
    SmspNhsNumberInvalidException,
    SmspNhsNumberNotVerifiedException,
    SmspNhsNumberNotNewStyleException,
)
from tests import login
from tests.demographics import (
    do_create_request,
    do_define_columns_post,
    do_submit,
    do_extract_data,
    do_upload_data_and_extract,
)

PMI_DETAILS = {
    'nhs_number': '4444444444',
    'uhl_system_number': 'S154367',
    'family_name': 'Smith',
    'given_name': 'Frances',
    'gender': 'F',
    'dob': parse('1976-01-01', dayfirst=True).date(),
    'date_of_death': parse('2010-03-04', dayfirst=True).date(),
    'postcode': 'LE5 9UH',
}

EXPECTED_PMI_DETAILS = DemographicsRequestPmiData(
    nhs_number=PMI_DETAILS['nhs_number'],
    uhl_system_number=PMI_DETAILS['uhl_system_number'],
    family_name=PMI_DETAILS['family_name'],
    given_name=PMI_DETAILS['given_name'],
    gender=PMI_DETAILS['gender'],
    date_of_birth=PMI_DETAILS['dob'],
    date_of_death=PMI_DETAILS['date_of_death'],
    postcode=PMI_DETAILS['postcode'],
)

PMI_DETAILS_2 = {
    'nhs_number': '5555555555',
    'uhl_system_number': 'S6543217',
    'family_name': 'Jones',
    'given_name': 'Martin',
    'gender': 'M',
    'dob': parse('1985-02-02', dayfirst=True).date(),
    'date_of_death': None,
    'postcode': 'LE3 9HY',
}

@pytest.fixture(autouse=True)
def cleanup_files(client):
    yield

    shutil.rmtree(
        current_app.config["FILE_UPLOAD_DIRECTORY"],
        ignore_errors=True,
    )


_MT_NHS_NUMBER = 0
_MT_SEARCH = 1
_MT_INSUFFICIENT = 2


@pytest.mark.parametrize(
    "data, messages, match_type, parameters",
    [
        # A valid example with all: Female
        (
            ['S1234567', '3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Jane', 'F', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Jane', ' F ', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        # A valid example with all: Male
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        # Missing NHS Number
        (
            ['S1234567', '', 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Dave',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        (
            ['S1234567', '    ', 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Dave',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        (
            ['S1234567', None, 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Dave',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        # Invalid NHS Number
        (
            ['S1234567', '3333987934', 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'nhs_number',
                    'message': 'Invalid format',
                }
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Dave',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        # Missing Family Name
        (
            ['S1234567', '', '', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_SEARCH,
            {
                'family_name': '',
                'given_name': 'Dave',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        (
            ['S1234567', '', '      ', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_SEARCH,
            {
                'family_name': '',
                'given_name': 'Dave',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        (
            ['S1234567', '', None, 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_SEARCH,
            {
                'family_name': '',
                'given_name': 'Dave',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        # Invalid Family Name
        (
            ['S1234567', '', 'N', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'family_name',
                    'message': 'Must be at least 2 characters',
                }
            ],
            _MT_SEARCH,
            {
                'family_name': '',
                'given_name': 'Dave',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        # Missing Given Name
        (
            ['S1234567', '', 'Smith', '', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': '',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        (
            ['S1234567', '', 'Smith', '      ', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': '',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        (
            ['S1234567', '', 'Smith', None, 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': '',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        # Invalid Given Name
        (
            ['S1234567', '', 'Smith', 'D', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'given_name',
                    'message': 'Must be at least 2 characters',
                }
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': '',
                'gender': SMSP_SEX_MALE,
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        # Missing Gender
        (
            ['S1234567', '3333333333', 'Smith', 'Frankie', '', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', '', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Missing value',
                },
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': '',
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', '    ', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Missing value',
                },
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': '',
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', None, '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Missing value',
                },
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': '',
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        # Invalid gender
        (
            ['S1234567', '', 'Smith', 'Dave', 'Fred', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Invalid format',
                },
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Missing value',
                },
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Dave',
                'gender': '',
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Dave', 'Malevolent', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Invalid format',
                },
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Missing value',
                },
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Dave',
                'gender': '',
                'dob': '19700101',
                'postcode': 'LE10 8HG',
            },
        ),
        # Invalid DOBs
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '31-Dec-1899', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Date out of range',
                },
                {
                    'type': 'error',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Missing required value',
                },
            ],
            _MT_INSUFFICIENT,
            {},
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '01-Jan-2100', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Date out of range',
                },
                {
                    'type': 'error',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Missing required value',
                },
            ],
            _MT_INSUFFICIENT,
            {},
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '01-Fred-2000', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Invalid date',
                },
                {
                    'type': 'error',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Missing required value',
                },
            ],
            _MT_INSUFFICIENT,
            {},
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '30-02-2000', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Invalid date',
                },
                {
                    'type': 'error',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Missing required value',
                },
            ],
            _MT_INSUFFICIENT,
            {},
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '13-13-2000', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Invalid date',
                },
                {
                    'type': 'error',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Missing required value',
                },
            ],
            _MT_INSUFFICIENT,
            {},
        ),
        # Valid DOBs
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '01-Jan-2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000101',
            },
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', 'January 1st 2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000101',
            },
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '01 January 2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000101',
            },
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', 'Monday 01 January 2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000101',
            },
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '01/02/2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000201',
            },
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '20000203', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000203',
            },
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Dave', 'M', '2000-02-03', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000203',
            },
        ),
        # Missing DOB
        (
            ['S1234567', '3333333333', 'Smith', 'Frankie', 'F', '', 'LE10 8HG'],
            [
                {
                    'type': 'error',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Missing required value',
                },
            ],
            _MT_INSUFFICIENT,
            {},
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Frankie', 'F', '     ', 'LE10 8HG'],
            [
                {
                    'type': 'error',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Missing required value',
                },
            ],
            _MT_INSUFFICIENT,
            {},
        ),
        (
            ['S1234567', '3333333333', 'Smith', 'Frankie', 'Female', None, 'LE10 8HG'],
            [
                {
                    'type': 'error',
                    'source': 'validation',
                    'scope': 'dob',
                    'message': 'Missing required value',
                },
            ],
            _MT_INSUFFICIENT,
            {},
        ),
        # Invalid postcodes
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'LE101 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'postcode',
                    'message': 'Invalid format',
                }
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': '',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', '10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'postcode',
                    'message': 'Invalid format',
                }
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': '',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'Female', '20000203', 'LE10 887HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'postcode',
                    'message': 'Invalid format',
                }
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': '',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'Female', '20000203', 'LE10A 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'postcode',
                    'message': 'Invalid format',
                }
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': '',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'Female', '20000203', 'LE10 8HG and something else'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'postcode',
                    'message': 'Invalid format',
                }
            ],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': '',
            },
        ),
        # Valid postcodes
        # - 149 Piccadilly, London. House of the Duke of Wellington
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'W1J 7NT'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'W1J 7NT',
            },
        ),
        # - 17 Burton Road Coton in the Elms, Derbyshire. The Black Horse Pub, possibly the furthest pub from the sea in the UK.
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'DE12 8HJ'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'DE12 8HJ',
            },
        ),
        # - Buckingham Palace
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'SW1A 1AA'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'SW1A 1AA',
            },
        ),
        # - covers 7 streets; the most in the UK
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'HD7 5UZ'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'HD7 5UZ',
            },
        ),
        # - the longest addresses in terms of numbers of elements
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'CH5 3QW'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'CH5 3QW',
            },
        ),
        # - the Post Town is CLARBESTON ROAD
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'SA63 4QJ'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'SA63 4QJ',
            },
        ),
        # - When all the premises get expanded you'll get the longest 'premise string' in the UK
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'W2 1JB'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'W2 1JB',
            },
        ),
        # - Devon and Cornwall Police vs Devon and Cornwall Constabulary
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'PL7 1RF'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'PL7 1RF',
            },
        ),
        # - special case Postcode for Girobank at Bootle
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'GIR 0AA'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'GIR 0AA',
            },
        ),
        # - You will find that 'towns and large villages' are classed as Localities; Jersey; the Isle of Man and Guernsey are the Post Towns.
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'JE3 1EP'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'JE3 1EP',
            },
        ),
        # - You will find that 'towns and large villages' are classed as Localities; Jersey; the Isle of Man and Guernsey are the Post Towns.
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'JE2 3XP'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'JE2 3XP',
            },
        ),
        # - You will find that 'towns and large villages' are classed as Localities; Jersey; the Isle of Man and Guernsey are the Post Towns.
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'IM9 4EB'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'IM9 4EB',
            },
        ),
        # - has no street
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'IM9 4AJ'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'IM9 4AJ',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'WC1A 1AA'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'WC1A 1AA',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'M1 1AA'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'M1 1AA',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'AB10 1JB'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'AB10 1JB',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', 'ZE3 9JZ'],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': 'ZE3 9JZ',
            },
        ),
        # Missing postcode
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', ''],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': '',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', '      '],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': '',
            },
        ),
        (
            ['S1234567', '', 'Smith', 'Frankie', 'F', '20000203', None],
            [],
            _MT_SEARCH,
            {
                'family_name': 'Smith',
                'given_name': 'Frankie',
                'gender': SMSP_SEX_FEMALE,
                'dob': '20000203',
                'postcode': '',
            },
        ),
    ],
)
def test__spine_lookup(client, faker, data, messages, match_type, parameters):

    drd = do_upload_data_and_extract(client, faker, data)

    with patch('identity.demographics.get_demographics_from_nhs_number') as mock_get_demographics_from_nhs_number, \
        patch('identity.demographics.get_demographics_from_search') as mock_get_demographics_from_search:

        response = MagicMock(
            title='Ms',
            forename='Janet',
            middlenames='Sarah',
            lastname='Smyth',
            postcode='LE8 10TY',
            address='1 The Road, Leicester',
            date_of_birth='01-Jan-1970',
            date_of_death='31-Dec-2010',
            is_deceased=True,
            current_gp_practice_code='G98764',
            sex='Female',
            nhs_number='3333333333',
        )
        mock_get_demographics_from_nhs_number.return_value = response
        mock_get_demographics_from_search.return_value = response

        spine_lookup(drd)

        if match_type == _MT_NHS_NUMBER:
            mock_get_demographics_from_nhs_number.assert_called_once_with(**parameters)
            mock_get_demographics_from_search.assert_not_called()
        elif match_type == _MT_SEARCH:
            mock_get_demographics_from_nhs_number.assert_not_called()
            mock_get_demographics_from_search.assert_called_once_with(**parameters)
        elif match_type == _MT_INSUFFICIENT:
            mock_get_demographics_from_nhs_number.assert_not_called()
            mock_get_demographics_from_search.assert_not_called()

    drd = DemographicsRequestData.query.get(drd.id)

    assert drd.processed_datetime is not None

    print(data)
    assert len(drd.messages) == len(messages)

    actual_messages = [
        {
            'type': m.type,
            'source': m.source,
            'scope': m.scope,
            'message': m.message,
        } for m in drd.messages
    ]

    assert actual_messages == messages

    if match_type != _MT_INSUFFICIENT:
        assert drd.response is not None
        assert drd.response.title == 'Ms'
        assert drd.response.forename == 'Janet'
        assert drd.response.middlenames == 'Sarah'
        assert drd.response.lastname == 'Smyth'
        assert drd.response.postcode == 'LE8 10TY'
        assert drd.response.address == '1 The Road, Leicester'
        assert drd.response.date_of_birth ==  datetime.date(1970,1,1)
        assert drd.response.date_of_death ==  datetime.date(2010,12,31)
        assert drd.response.is_deceased == True
        assert drd.response.current_gp_practice_code == 'G98764'


@pytest.mark.parametrize(
    "exception_class",
    [
        (SmspNoMatchException),
        (SmspMultipleMatchesException),
        (SmspNhsNumberSupersededException),
        (SmspNhsNumberInvalidException),
        (SmspNhsNumberNotVerifiedException),
        (SmspNhsNumberNotNewStyleException),
    ],
)
def test__spine_nhs_lookup_exceptions(client, faker, exception_class):
    drd = do_upload_data_and_extract(client, faker, ['S1234567', '3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    with patch('identity.demographics.get_demographics_from_nhs_number') as mock_get_demographics_from_nhs_number:

        mock_get_demographics_from_nhs_number.side_effect = exception_class()

        spine_lookup(drd)

    drd = DemographicsRequestData.query.get(drd.id)

    assert drd.processed_datetime is not None
    assert len(drd.messages) == 1

    assert drd.messages[0].type == 'error'
    assert drd.messages[0].source == 'spine'
    assert drd.messages[0].scope == 'request'
    assert drd.messages[0].message == exception_class().message


@pytest.mark.parametrize(
    "exception_class",
    [
        (SmspNoMatchException),
        (SmspMultipleMatchesException),
        (SmspNhsNumberSupersededException),
        (SmspNhsNumberInvalidException),
        (SmspNhsNumberNotVerifiedException),
        (SmspNhsNumberNotNewStyleException),
    ],
)
def test__spine_search_exceptions(client, faker, exception_class):
    drd = do_upload_data_and_extract(client, faker, ['S1234567', '', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    with patch('identity.demographics.get_demographics_from_search') as mock_get_demographics_from_search:

        mock_get_demographics_from_search.side_effect = exception_class()

        spine_lookup(drd)

    drd = DemographicsRequestData.query.get(drd.id)

    assert drd.processed_datetime is not None
    assert len(drd.messages) == 1

    assert drd.messages[0].type == 'error'
    assert drd.messages[0].source == 'spine'
    assert drd.messages[0].scope == 'request'
    assert drd.messages[0].message == exception_class().message


def test__spine_nhs_lookup_response(client, faker):
    drd = do_upload_data_and_extract(client, faker, ['S1234567', '3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    with patch('identity.demographics.get_demographics_from_nhs_number') as mock_get_demographics_from_nhs_number:

        mock_get_demographics_from_nhs_number.return_value = MagicMock(
            title='Ms',
            forename='Janet',
            middlenames='Sarah',
            lastname='Smyth',
            postcode='LE8 10TY',
            address='1 The Road, Leicester',
            date_of_birth='01-Jan-1970',
            date_of_death='31-Dec-2010',
            is_deceased=True,
            current_gp_practice_code='G98764',
            sex='Female',
            nhs_number='3333333333',
        )

        spine_lookup(drd)

    drd = DemographicsRequestData.query.get(drd.id)

    assert drd.processed_datetime is not None
    assert len(drd.messages) == 0

    assert drd.response is not None
    assert drd.response.title == 'Ms'
    assert drd.response.forename == 'Janet'
    assert drd.response.middlenames == 'Sarah'
    assert drd.response.lastname == 'Smyth'
    assert drd.response.postcode == 'LE8 10TY'
    assert drd.response.address == '1 The Road, Leicester'
    assert drd.response.date_of_birth == datetime.date(1970,1,1)
    assert drd.response.date_of_death == datetime.date(2010,12,31)
    assert drd.response.is_deceased == True
    assert drd.response.current_gp_practice_code == 'G98764'


def test__spine_search_response(client, faker):
    drd = do_upload_data_and_extract(client, faker, ['S1234567', '', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    with patch('identity.demographics.get_demographics_from_search') as mock_get_demographics_from_search:

        mock_get_demographics_from_search.return_value = MagicMock(
            title='Ms',
            forename='Janet',
            middlenames='Sarah',
            lastname='Smyth',
            postcode='LE8 10TY',
            address='1 The Road, Leicester',
            date_of_birth='01-Jan-1970',
            date_of_death='31-Dec-2010',
            is_deceased=True,
            current_gp_practice_code='G98764',
            sex='Female',
            nhs_number='3333333333',
        )

        spine_lookup(drd)

    drd = DemographicsRequestData.query.get(drd.id)

    assert drd.processed_datetime is not None
    assert len(drd.messages) == 0

    assert drd.response is not None
    assert drd.response.title == 'Ms'
    assert drd.response.forename == 'Janet'
    assert drd.response.middlenames == 'Sarah'
    assert drd.response.lastname == 'Smyth'
    assert drd.response.postcode == 'LE8 10TY'
    assert drd.response.address == '1 The Road, Leicester'
    assert drd.response.date_of_birth == datetime.date(1970,1,1)
    assert drd.response.date_of_death == datetime.date(2010,12,31)
    assert drd.response.is_deceased == True
    assert drd.response.current_gp_practice_code == 'G98764'
