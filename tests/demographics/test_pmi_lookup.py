# -*- coding: utf-8 -*-

import pytest
import datetime
from dateutil.parser import parse
from identity.demographics.model import (
    DemographicsRequestPmiData,
    DemographicsRequestData,
)
from identity.demographics import extract_pre_pmi_details


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
