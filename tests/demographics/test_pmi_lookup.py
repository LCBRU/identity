# -*- coding: utf-8 -*-

import pytest
import datetime
from dateutil.parser import parse
from identity.demographics.model import (
    DemographicsRequestPmiData,
    DemographicsRequestData,
)
from identity.demographics import extract_pre_pmi_details

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

def test__extract_post_pmi_details__nhs_number_found(client, faker, mock_pmi_engine):
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [PMI_DETAILS]

    drd = DemographicsRequestData()
    drd.nhs_number = '3333333333'

    result = extract_pre_pmi_details(drd)

    mock_pmi_engine.return_value.__enter__.return_value.execute.assert_called_once()
    

# def test__get_pmi_details__correct(client, faker):
#     with patch('identity.demographics.pmi_engine') as mock_engine:
#         mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [PMI_DETAILS]

#         drd = DemographicsRequestData()
#         drd.nhs_number = '3333333333'

#         result = get_pmi_details(drd)

#         mock_engine.return_value.__enter__.return_value.execute.assert_called_once()
    
#     assert drd. == EXPECTED_PMI_DETAILS


# def test__get_pmi_details__not_found(client, faker):
#     with patch('identity.demographics.pmi_engine') as mock_engine:
#         mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = []

#         drd = DemographicsRequestData()
#         drd.nhs_number = '100'

#         result = get_pmi_details(drd)

#         mock_engine.return_value.__enter__.return_value.execute.assert_called_once()
    
#     assert result is None


# def test__get_pmi_details__multiple_found(client, faker):
#     with patch('identity.demographics.pmi_engine') as mock_engine:
#         mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [PMI_DETAILS, PMI_DETAILS_2]

#         drd = DemographicsRequestData()
#         drd.nhs_number = '100'

#         with pytest.raises(Exception):
#             get_pmi_details(drd)

#         mock_engine.return_value.__enter__.return_value.execute.assert_called_once()


# def test__get_pmi_details__multi_ids__both_not_found(client, faker):
#     with patch('identity.demographics.pmi_engine') as mock_engine:
#         mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = []

#         drd = DemographicsRequestData()
#         drd.nhs_number = '100'
#         drd.uhl_system_number = '200'

#         result = get_pmi_details(drd)

#         assert mock_engine.return_value.__enter__.return_value.execute.call_count == 2
    
#     assert result is None


# def test__get_pmi_details__multi_ids__first_found(client, faker):
#     with patch('identity.demographics.pmi_engine') as mock_engine:
#         mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[PMI_DETAILS], []]

#         drd = DemographicsRequestData()
#         drd.nhs_number = '100'
#         drd.uhl_system_number = '200'

#         result = get_pmi_details(drd)

#         assert mock_engine.return_value.__enter__.return_value.execute.call_count == 2
    
#     assert result == EXPECTED_PMI_DETAILS


# def test__get_pmi_details__multi_ids__second_found(client, faker):
#     with patch('identity.demographics.pmi_engine') as mock_engine:
#         mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[], [PMI_DETAILS]]

#         drd = DemographicsRequestData()
#         drd.nhs_number = '100'
#         drd.uhl_system_number = '200'

#         result = get_pmi_details(drd)

#         assert mock_engine.return_value.__enter__.return_value.execute.call_count == 2
    
#     assert result == EXPECTED_PMI_DETAILS


# def test__get_pmi_details__multi_ids__mismatch(client, faker):
#     with patch('identity.demographics.pmi_engine') as mock_engine:
#         mock_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[PMI_DETAILS_2], [PMI_DETAILS]]

#         drd = DemographicsRequestData()
#         drd.nhs_number = '100'
#         drd.uhl_system_number = '200'

#         with pytest.raises(Exception):
#             get_pmi_details(drd)

#         assert mock_engine.return_value.__enter__.return_value.execute.call_count == 2


# def test__extract_pmi_details(client, faker):
#     drd = do_upload_data_and_extract(client, faker, ['S1234567', '3333333333', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

#     with patch('identity.demographics.get_pmi_details') as mock_get_pmi_details:
#         mock_get_pmi_details.return_value = EXPECTED_PMI_DETAILS

#         extract_pre_pmi_details(drd.demographics_request.id)

#     drd = DemographicsRequestData.query.get(drd.id)

#     assert drd.pmi_data is not None
#     assert len(drd.messages) == 0

#     assert drd.pmi_data == EXPECTED_PMI_DETAILS
