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
    extract_pmi_details,
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
    'nhs_number': '12345678',
    'uhl_system_number': 'S154367',
    'family_name': 'Smith',
    'given_name': 'Frances',
    'gender': 'F',
    'dob': parse('1976-01-01', dayfirst=True).date(),
    'postcode': 'LE5 9UH',
}

EXPECTED_PMI_DETAILS = DemographicsRequestPmiData(
    nhs_number=PMI_DETAILS['nhs_number'],
    uhl_system_number=PMI_DETAILS['uhl_system_number'],
    family_name=PMI_DETAILS['family_name'],
    given_name=PMI_DETAILS['given_name'],
    gender=PMI_DETAILS['gender'],
    date_of_birth=PMI_DETAILS['dob'],
    postcode=PMI_DETAILS['postcode'],
)

PMI_DETAILS_2 = {
    'nhs_number': '87654321',
    'uhl_system_number': 'S6543217',
    'family_name': 'Jones',
    'given_name': 'Martin',
    'gender': 'M',
    'dob': parse('1985-02-02', dayfirst=True).date(),
    'postcode': 'LE3 9HY',
}

@pytest.fixture(autouse=True)
def cleanup_files(client):
    yield

    shutil.rmtree(
        current_app.config["FILE_UPLOAD_DIRECTORY"],
        ignore_errors=True,
    )


def test__get_pmi_details__correct(client, faker):
    with patch('identity.demographics.pmi_engine') as mock_engine:
        mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [PMI_DETAILS]

        result = get_pmi_details('100')

        mock_engine.return_value.__enter__.return_value.execute.assert_called_once()
    
    assert result == EXPECTED_PMI_DETAILS


def test__get_pmi_details__not_found(client, faker):
    with patch('identity.demographics.pmi_engine') as mock_engine:
        mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = []

        result = get_pmi_details('100')

        mock_engine.return_value.__enter__.return_value.execute.assert_called_once()
    
    assert result is None


def test__get_pmi_details__multiple_found(client, faker):
    with patch('identity.demographics.pmi_engine') as mock_engine:
        mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [PMI_DETAILS, PMI_DETAILS_2]

        with pytest.raises(Exception):
            get_pmi_details('100')

        mock_engine.return_value.__enter__.return_value.execute.assert_called_once()


def test__get_pmi_details__multi_ids__both_not_found(client, faker):
    with patch('identity.demographics.pmi_engine') as mock_engine:
        mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = []

        result = get_pmi_details('100', '200')

        assert mock_engine.return_value.__enter__.return_value.execute.call_count == 2
    
    assert result is None


def test__get_pmi_details__multi_ids__first_found(client, faker):
    with patch('identity.demographics.pmi_engine') as mock_engine:
        mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[PMI_DETAILS], []]

        result = get_pmi_details('100', '200')

        assert mock_engine.return_value.__enter__.return_value.execute.call_count == 2
    
    assert result == EXPECTED_PMI_DETAILS


def test__get_pmi_details__multi_ids__second_found(client, faker):
    with patch('identity.demographics.pmi_engine') as mock_engine:
        mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[], [PMI_DETAILS]]

        result = get_pmi_details('100', '200')

        assert mock_engine.return_value.__enter__.return_value.execute.call_count == 2
    
    assert result == EXPECTED_PMI_DETAILS


def test__get_pmi_details__multi_ids__mismatch(client, faker):
    with patch('identity.demographics.pmi_engine') as mock_engine:
        mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[PMI_DETAILS_2], [PMI_DETAILS]]

        with pytest.raises(Exception):
            get_pmi_details('100', '200')

        assert mock_engine.return_value.__enter__.return_value.execute.call_count == 2


def test__extract_pmi_details(client, faker):
    drd = do_upload_data_and_extract(client, faker, ['3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    with patch('identity.demographics.get_pmi_details') as mock_get_pmi_details:
        mock_get_pmi_details.return_value = EXPECTED_PMI_DETAILS

        extract_pmi_details(drd.demographics_request.id)

    drd = DemographicsRequestData.query.get(drd.id)

    assert drd.pmi_data is not None
    assert len(drd.messages) == 0

    assert drd.pmi_data == EXPECTED_PMI_DETAILS


@pytest.mark.parametrize(
    "extension,header_count,column_count,row_count",
    [
        ('csv', 10, 10, 10),
        ('xlsx', 10, 10, 10),
        ('csv', 10, 9, 10),
        ('xlsx', 10, 9, 10),
        ('csv', 9, 10, 10),
        ('xlsx', 9, 10, 10),
        ('csv', 10, 10, 0),
        ('xlsx', 10, 10, 0),
    ],
)
def test__extract_data(client, faker, extension, header_count, column_count, row_count):
    user = login(client, faker)

    headers = faker.pylist(header_count, False, 'str')

    expected_data = [faker.pylist(column_count, False, 'str') for _ in range(row_count)]

    dr = do_create_request(client, faker, user, headers, expected_data, extension)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5])

    do_submit(client, dr.id)

    do_extract_data(dr.id)

    dr = DemographicsRequest.query.get(dr.id)
    assert len(dr.data) == len(expected_data)
    assert dr.data_extracted == True
    assert dr.data_extracted_datetime is not None

    for e, a in zip(expected_data, dr.data):
        assert e[0] == a.nhs_number
        assert e[1] == a.family_name
        assert e[2] == a.given_name
        assert e[3] == a.gender
        assert e[4] == a.dob
        assert e[5] == a.postcode


_MT_NHS_NUMBER = 0
_MT_SEARCH = 1
_MT_INSUFFICIENT = 2


@pytest.mark.parametrize(
    "data, messages, match_type, parameters",
    [
        # A valid example with all: Female
        (
            ['3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        (
            ['3333333333', 'Smith', 'Jane', 'F', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        (
            ['3333333333', 'Smith', 'Jane', ' F ', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        # A valid example with all: Male
        (
            ['3333333333', 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        (
            ['3333333333', 'Smith', 'Dave', 'M', '01-Jan-1970', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        # Missing NHS Number
        (
            ['', 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['    ', 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            [None, 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['3333987934', 'Smith', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['', '', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['', '      ', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['', None, 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['', 'N', 'Dave', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['', 'Smith', '', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['', 'Smith', '      ', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['', 'Smith', None, 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['', 'Smith', 'D', 'Male', '01-Jan-1970', 'LE10 8HG'],
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
            ['3333333333', 'Smith', 'Frankie', '', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Missing value',
                },
            ],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '19700101',
            },
        ),
        (
            ['', 'Smith', 'Frankie', '', '01-Jan-1970', 'LE10 8HG'],
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
            ['', 'Smith', 'Frankie', '    ', '01-Jan-1970', 'LE10 8HG'],
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
            ['', 'Smith', 'Frankie', None, '01-Jan-1970', 'LE10 8HG'],
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
            ['', 'Smith', 'Dave', 'Fred', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Invalid format',
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
            ['', 'Smith', 'Dave', 'Malevolent', '01-Jan-1970', 'LE10 8HG'],
            [
                {
                    'type': 'warning',
                    'source': 'validation',
                    'scope': 'gender',
                    'message': 'Invalid format',
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
            ['3333333333', 'Smith', 'Dave', 'M', '31-Dec-1899', 'LE10 8HG'],
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
            ['3333333333', 'Smith', 'Dave', 'M', '01-Jan-2100', 'LE10 8HG'],
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
            ['3333333333', 'Smith', 'Dave', 'M', '01-Fred-2000', 'LE10 8HG'],
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
            ['3333333333', 'Smith', 'Dave', 'M', '30-02-2000', 'LE10 8HG'],
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
            ['3333333333', 'Smith', 'Dave', 'M', '13-13-2000', 'LE10 8HG'],
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
            ['3333333333', 'Smith', 'Dave', 'M', '01-Jan-2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000101',
            },
        ),
        (
            ['3333333333', 'Smith', 'Dave', 'M', 'January 1st 2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000101',
            },
        ),
        (
            ['3333333333', 'Smith', 'Dave', 'M', '01 January 2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000101',
            },
        ),
        (
            ['3333333333', 'Smith', 'Dave', 'M', 'Monday 01 January 2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000101',
            },
        ),
        (
            ['3333333333', 'Smith', 'Dave', 'M', '01/02/2000', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000201',
            },
        ),
        (
            ['3333333333', 'Smith', 'Dave', 'M', '20000203', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000203',
            },
        ),
        (
            ['3333333333', 'Smith', 'Dave', 'M', '2000-02-03', 'LE10 8HG'],
            [],
            _MT_NHS_NUMBER,
            {
                'nhs_number': '3333333333',
                'dob': '20000203',
            },
        ),
        # Missing DOB
        (
            ['3333333333', 'Smith', 'Frankie', 'F', '', 'LE10 8HG'],
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
            ['3333333333', 'Smith', 'Frankie', 'F', '     ', 'LE10 8HG'],
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
            ['3333333333', 'Smith', 'Frankie', 'Female', None, 'LE10 8HG'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'LE101 8HG'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', '10 8HG'],
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
            ['', 'Smith', 'Frankie', 'Female', '20000203', 'LE10 887HG'],
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
            ['', 'Smith', 'Frankie', 'Female', '20000203', 'LE10A 8HG'],
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
            ['', 'Smith', 'Frankie', 'Female', '20000203', 'LE10 8HG and something else'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'W1J 7NT'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'DE12 8HJ'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'SW1A 1AA'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'HD7 5UZ'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'CH5 3QW'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'SA63 4QJ'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'W2 1JB'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'PL7 1RF'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'GIR 0AA'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'JE3 1EP'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'JE2 3XP'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'IM9 4EB'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'IM9 4AJ'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'WC1A 1AA'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'M1 1AA'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'AB10 1JB'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', 'ZE3 9JZ'],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', ''],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', '      '],
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
            ['', 'Smith', 'Frankie', 'F', '20000203', None],
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
    drd = do_upload_data_and_extract(client, faker, ['3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

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
    drd = do_upload_data_and_extract(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

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
    drd = do_upload_data_and_extract(client, faker, ['3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

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
    drd = do_upload_data_and_extract(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

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


def test__process_demographics_request_data(client, faker):
    drd = do_upload_data_and_extract(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    with patch('identity.demographics.spine_lookup') as mock_spine_lookup, \
        patch('identity.demographics.schedule_lookup_tasks') as mock_schedule_lookup_tasks, \
        patch('identity.demographics.log_exception') as mock_log_exception:

        process_demographics_request_data(drd.id, drd.demographics_request.id)

        mock_spine_lookup.assert_called_once_with(drd)
        mock_schedule_lookup_tasks.assert_called_once_with(
            drd.demographics_request.id,
        )
        mock_log_exception.assert_not_called()


def test__process_demographics_request_data_exception(client, faker):
    drd = do_upload_data_and_extract(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    with patch('identity.demographics.spine_lookup') as mock_spine_lookup, \
        patch('identity.demographics.schedule_lookup_tasks') as mock_schedule_lookup_tasks, \
        patch('identity.demographics.log_exception') as mock_log_exception:

        e = Exception()

        mock_spine_lookup.side_effect = e
        process_demographics_request_data(drd.id, drd.demographics_request.id)

        mock_spine_lookup.assert_called_once_with(drd)
        mock_schedule_lookup_tasks.assert_not_called()
        mock_log_exception.assert_called_once_with(e)


def test__process_demographics_request_data__data_not_found(client, faker):
    drd = do_upload_data_and_extract(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    with patch('identity.demographics.spine_lookup') as mock_spine_lookup, \
        patch('identity.demographics.schedule_lookup_tasks') as mock_schedule_lookup_tasks, \
        patch('identity.demographics.log_exception') as mock_log_exception:

        process_demographics_request_data(drd.id + 1, drd.demographics_request.id) # ID that doesn't exist

        mock_spine_lookup.assert_not_called()
        mock_schedule_lookup_tasks.assert_called_once_with(
            drd.demographics_request.id,
        )
        assert mock_log_exception.called == 1


@pytest.mark.parametrize(
    "data, lookup_response, extension",
    [
        (
            [
                ['3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'],
            ],
            [
                {
                    'nhs_number': '3333333333',
                    'sex': 'Female',
                    'title': 'Ms',
                    'forename': 'Janet',
                    'middlenames': 'Sarah',
                    'lastname': 'Smyth',
                    'postcode': 'LE8 10TY',
                    'address': '1 The Road, Leicester',
                    'date_of_birth': '01-Jan-1970',
                    'date_of_death': '31-Dec-2010',
                    'is_deceased': True,
                    'current_gp_practice_code': 'G98764',
                    'messages': [],
                    'expected_message': '',
                },
            ],
            'csv',
        ),
        (
            [
                ['3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'],
                ['4444444444', 'Jones', 'Ben', 'Male', '01-Jan-1971', 'LE8 1HG'],
            ],
            [
                {
                    'nhs_number': '3333333333',
                    'sex': 'Female',
                    'title': 'Ms',
                    'forename': 'Janet',
                    'middlenames': 'Sarah',
                    'lastname': 'Smyth',
                    'postcode': 'LE8 10TY',
                    'address': '1 The Road, Leicester',
                    'date_of_birth': '01-Jan-1970',
                    'date_of_death': '31-Dec-2010',
                    'is_deceased': True,
                    'current_gp_practice_code': 'G98764',
                    'messages': [
                        {
                            'type': 'error',
                            'source': 'spine',
                            'scope': 'data',
                            'message': 'Oh No!',
                        },
                        {
                            'type': 'warning',
                            'source': 'validation',
                            'scope': 'request',
                            'message': 'Something is not quite right',
                        },
                    ],
                    'expected_message': 'spine error in data: Oh No!; validation warning in request: Something is not quite right',
                },
                {
                    'nhs_number': '3333333333',
                    'sex': 'Male',
                    'title': 'Mr',
                    'forename': 'Benjamin',
                    'middlenames': 'Alberto',
                    'lastname': 'Jones',
                    'postcode': 'LE8 1HGA',
                    'address': '2 The Road, Leicester',
                    'date_of_birth': '01-Jan-1971',
                    'date_of_death': '',
                    'is_deceased': False,
                    'current_gp_practice_code': 'G98724',
                    'messages': [
                        {
                            'type': 'error',
                            'source': 'spine',
                            'scope': 'data',
                            'message': 'Something is amiss',
                        },
                    ],
                    'expected_message': 'spine error in data: Something is amiss',
                },
            ],
            'csv',
        ),
        (
            [
                ['3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'],
            ],
            [
                {
                    'nhs_number': '3333333333',
                    'sex': 'Female',
                    'title': 'Ms',
                    'forename': 'Janet',
                    'middlenames': 'Sarah',
                    'lastname': 'Smyth',
                    'postcode': 'LE8 10TY',
                    'address': '1 The Road, Leicester',
                    'date_of_birth': '01-Jan-1970',
                    'date_of_death': '31-Dec-2010',
                    'is_deceased': True,
                    'current_gp_practice_code': 'G98764',
                    'messages': [],
                    'expected_message': '',
                },
            ],
            'xlsx',
        ),
        (
            [
                ['3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'],
                ['4444444444', 'Jones', 'Ben', 'Male', '01-Jan-1971', 'LE8 1HG'],
            ],
            [
                {
                    'nhs_number': '3333333333',
                    'sex': 'Female',
                    'title': 'Ms',
                    'forename': 'Janet',
                    'middlenames': 'Sarah',
                    'lastname': 'Smyth',
                    'postcode': 'LE8 10TY',
                    'address': '1 The Road, Leicester',
                    'date_of_birth': '01-Jan-1970',
                    'date_of_death': '31-Dec-2010',
                    'is_deceased': True,
                    'current_gp_practice_code': 'G98764',
                    'messages': [
                        {
                            'type': 'error',
                            'source': 'spine',
                            'scope': 'data',
                            'message': 'Oh No!',
                        },
                        {
                            'type': 'warning',
                            'source': 'validation',
                            'scope': 'request',
                            'message': 'Something is not quite right',
                        },
                    ],
                    'expected_message': 'spine error in data: Oh No!; validation warning in request: Something is not quite right',
                },
                {
                    'nhs_number': '3333333333',
                    'sex': 'Male',
                    'title': 'Mr',
                    'forename': 'Benjamin',
                    'middlenames': 'Alberto',
                    'lastname': 'Jones',
                    'postcode': 'LE8 1HGA',
                    'address': '2 The Road, Leicester',
                    'date_of_birth': '01-Jan-1971',
                    'date_of_death': '',
                    'is_deceased': False,
                    'current_gp_practice_code': 'G98724',
                    'messages': [
                        {
                            'type': 'error',
                            'source': 'spine',
                            'scope': 'data',
                            'message': 'Something is amiss',
                        },
                    ],
                    'expected_message': 'spine error in data: Something is amiss',
                },
            ],
            'xlsx',
        ),
    ]
)
def test__produce_demographics_result(client, faker, data, lookup_response, extension):

    user = login(client, faker)

    headers = ['nhs_number', 'family_name', 'given_name', 'gender', 'dob', 'postcode']

    dr = do_create_request(client, faker, user, headers, data, extension)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5])
    do_submit(client, dr.id)
    do_extract_data(dr.id)

    with patch('identity.demographics.get_pmi_details') as mock_get_pmi_details:
        mock_get_pmi_details.side_effect = [
            DemographicsRequestPmiData(
                nhs_number=PMI_DETAILS['nhs_number'],
                uhl_system_number=PMI_DETAILS['uhl_system_number'],
                family_name=PMI_DETAILS['family_name'],
                given_name=PMI_DETAILS['given_name'],
                gender=PMI_DETAILS['gender'],
                date_of_birth=PMI_DETAILS['dob'],
                postcode=PMI_DETAILS['postcode'],
            ) for _ in range(4)]
        
        extract_pmi_details(dr.id)

    for d, l in zip(dr.data, lookup_response):

        with patch('identity.demographics.get_demographics_from_nhs_number') as mock_get_demographics_from_nhs_number:
            mock_get_demographics_from_nhs_number.return_value = MagicMock(**l)

            spine_lookup(d)

            for m in l['messages']:
                d.messages.append(DemographicsRequestDataMessage(**m))

    with patch('identity.demographics.email') as mock_email:

        produce_demographics_result(dr.id)
        assert mock_email.called

    dr = DemographicsRequest.query.get(dr.id)

    assert dr.result_created_datetime is not None
    assert dr.result_created

    assert os.path.isfile(dr.result_filepath)

    for row, expected in zip(dr.iter_result_rows(), lookup_response):
        assert row['spine_title'] == expected['title']
        assert row['spine_forename'] == expected['forename']
        assert row['spine_middlenames'] == expected['middlenames']
        assert row['spine_lastname'] == expected['lastname']
        assert row['spine_postcode'] == expected['postcode']
        assert row['spine_address'] == expected['address']
        assert row['spine_date_of_birth'] == expected['date_of_birth']
        assert row['spine_date_of_death'] or '' == expected['date_of_death']
        assert (row['spine_is_deceased'] == 'True') == expected['is_deceased']
        assert row['spine_current_gp_practice_code'] == expected['current_gp_practice_code']
        assert row['spine_message'] or '' == expected['expected_message']

        assert row['pmi_nhs_number'] == PMI_DETAILS['nhs_number']
        assert row['pmi_uhl_system_number'] == PMI_DETAILS['uhl_system_number']
        assert row['pmi_family_name'] == PMI_DETAILS['family_name']
        assert row['pmi_given_name'] == PMI_DETAILS['given_name']
        assert row['pmi_gender'] == PMI_DETAILS['gender']
        assert row['pmi_dob'] if isinstance(row['pmi_dob'], datetime.date) else parse(row['pmi_dob'], dayfirst=True).date() == PMI_DETAILS['dob']
        assert row['pmi_postcode'] == PMI_DETAILS['postcode']
