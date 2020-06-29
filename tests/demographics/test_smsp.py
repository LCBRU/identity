# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch, MagicMock, call
from identity.demographics.smsp import (
    get_demographics_from_search,
    _SMSP_OK,
    _SMSP_ERR_NO_MATCH,
    SmspMultipleMatchesException,
)


def test__get_demographics_from_search__called_with_values(client, faker):
    with patch('identity.demographics.smsp._get_demographics_client') as mock_client:

        mock_client.return_value.service.getPatientBySearch.side_effect = [MagicMock(
            responseCode=_SMSP_OK,
            nhs_number='2222222222',
        )]
        
        get_demographics_from_search(
            family_name= 'Smith',
            given_name = 'Val',
            gender = 'M',
            dob = '01-Jan-1980',
            postcode = 'LE6 9YH',
        )

        mock_client.return_value.service.getPatientBySearch.assert_called_once_with(
            familyName= 'Smith',
            givenName = 'Val',
            gender = 'M',
            dob = '01-Jan-1980',
            postcode = 'LE6 9YH',
        )


def test__get_demographics_from_search__null_postcode__called_with_empty_postcode(client, faker):
    with patch('identity.demographics.smsp._get_demographics_client') as mock_client:

        mock_client.return_value.service.getPatientBySearch.side_effect = [MagicMock(
            responseCode=_SMSP_OK,
            nhs_number='2222222222',
        )]
        
        get_demographics_from_search(
            family_name= 'Smith',
            given_name = 'Val',
            gender = 'M',
            dob = '01-Jan-1980',
            postcode = None,
        )

        mock_client.return_value.service.getPatientBySearch.assert_called_once_with(
            familyName= 'Smith',
            givenName = 'Val',
            gender = 'M',
            dob = '01-Jan-1980',
            postcode = '',
        )


def test__get_demographics_from_search__null_given_name__called_with_empty_given_name(client, faker):
    with patch('identity.demographics.smsp._get_demographics_client') as mock_client:

        mock_client.return_value.service.getPatientBySearch.side_effect = [MagicMock(
            responseCode=_SMSP_OK,
            nhs_number='2222222222',
        )]
        
        get_demographics_from_search(
            family_name= 'Smith',
            given_name = None,
            gender = 'M',
            dob = '01-Jan-1980',
            postcode = 'LE6 9YH',
        )

        mock_client.return_value.service.getPatientBySearch.assert_called_once_with(
            familyName= 'Smith',
            givenName = '',
            gender = 'M',
            dob = '01-Jan-1980',
            postcode = 'LE6 9YH',
        )


def test__get_demographics_from_search__not_found__tries_with_no_postcode_and_forename(client, faker):
    with patch('identity.demographics.smsp._get_demographics_client') as mock_client:

        mock_client.return_value.service.getPatientBySearch.side_effect = [MagicMock(
            responseCode=rc,
            nhs_number='2222222222',
        ) for rc in [_SMSP_ERR_NO_MATCH, _SMSP_ERR_NO_MATCH, _SMSP_ERR_NO_MATCH, _SMSP_OK]]
        
        get_demographics_from_search(
            family_name= 'Smith',
            given_name = 'Val',
            gender = 'M',
            dob = '01-Jan-1980',
            postcode = 'LE6 9YH',
        )

        mock_client.return_value.service.getPatientBySearch.assert_has_calls([
            call(
                familyName= 'Smith',
                givenName = 'Val',
                gender = 'M',
                dob = '01-Jan-1980',
                postcode = 'LE6 9YH',
            ),
            call(
                familyName= 'Smith',
                givenName = 'Val',
                gender = 'M',
                dob = '01-Jan-1980',
                postcode = '',
            ),
            call(
                familyName= 'Smith',
                givenName = '',
                gender = 'M',
                dob = '01-Jan-1980',
                postcode = 'LE6 9YH',
            ),
            call(
                familyName= 'Smith',
                givenName = '',
                gender = 'M',
                dob = '01-Jan-1980',
                postcode = '',
            ),
        ])
