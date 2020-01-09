# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch, MagicMock
from identity.demographics.smsp import (
    get_demographics_from_search,
    _SMSP_OK,
    SmspMultipleMatchesException,
)


def test__get_demographics_from_search__missing_gender_returns_multiple(client, faker):
    with patch('identity.demographics.smsp._get_demographics_client') as mock_client:

        mock_client.return_value.service.getPatientBySearch.side_effect = [
            MagicMock(
                responseCode=_SMSP_OK,
                nhs_number=nhs,
            ) for nhs in ['2222222222', '3333333333']]
        
        with pytest.raises(SmspMultipleMatchesException):
            get_demographics_from_search(
                family_name= 'Smith',
                given_name = 'Val',
                gender = '',
                dob = '',
                postcode = '',
            )
