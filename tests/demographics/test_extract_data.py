import contextlib
import os
import pytest
from identity.demographics import extract_data
from identity.demographics.model import (
    DemographicsRequest,
)
from identity.services.validators import parse_date
from tests import login
from tests.demographics import (
    DemographicsTestHelper,
)


@pytest.mark.parametrize(
    "extension,row_count",
    [
        ('csv', 10),
        ('xlsx', 10),
        ('xls', 10),
        ('csv', 0),
        ('xlsx', 0),
        ('xls', 0),
    ],
)
def test__extract_data__normal(client, faker, extension, row_count, mock_schedule_lookup_tasks, mock_log_exception):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=row_count, extension=extension)
    dr = dth.get_demographics_request__data_extraction()

    extract_data(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)
    mock_log_exception.assert_not_called()

    assert len(actual.data) == row_count
    assert actual.data_extracted == True
    assert actual.data_extracted_datetime is not None

    for e, a in zip(dth._person_details, actual.data):
        assert e['uhl_system_number'] == a.uhl_system_number
        assert e['nhs_number'] == a.nhs_number
        assert e['family_name'] == a.family_name
        assert e['given_name'] == a.given_name
        assert e['gender'] == a.gender
        assert parse_date(e['date_of_birth']) == parse_date(a.dob)
        assert e['postcode'] == a.postcode
    
    _remove_files(dr)


@pytest.mark.parametrize(
    "extension,column_headings",
    [
        ('csv', ['nhs_number', 'family_name', 'given_name', 'gender', 'date_of_birth', 'postcode']),
        ('xlsx', ['nhs_number', 'family_name', 'given_name', 'gender', 'date_of_birth', 'postcode']),
        ('xls', ['nhs_number', 'family_name', 'given_name', 'gender', 'date_of_birth', 'postcode']),
        ('csv', ['uhl_system_number', 'family_name', 'given_name', 'gender', 'date_of_birth', 'postcode']),
        ('xlsx', ['uhl_system_number', 'family_name', 'given_name', 'gender', 'date_of_birth', 'postcode']),
        ('xls', ['uhl_system_number', 'family_name', 'given_name', 'gender', 'date_of_birth', 'postcode']),
        ('csv', ['uhl_system_number', 'nhs_number', 'given_name', 'gender', 'date_of_birth', 'postcode']),
        ('xlsx', ['uhl_system_number', 'nhs_number', 'given_name', 'gender', 'date_of_birth', 'postcode']),
        ('xls', ['uhl_system_number', 'nhs_number', 'given_name', 'gender', 'date_of_birth', 'postcode']),
        ('csv', ['uhl_system_number', 'nhs_number', 'family_name', 'gender', 'date_of_birth', 'postcode']),
        ('xlsx', ['uhl_system_number', 'nhs_number', 'family_name', 'gender', 'date_of_birth', 'postcode']),
        ('xls', ['uhl_system_number', 'nhs_number', 'family_name', 'gender', 'date_of_birth', 'postcode']),
        ('csv', ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'date_of_birth', 'postcode']),
        ('xlsx', ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'date_of_birth', 'postcode']),
        ('xls', ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'date_of_birth', 'postcode']),
        ('csv', ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'postcode']),
        ('xlsx', ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'postcode']),
        ('xls', ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'postcode']),
        ('csv', ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'date_of_birth']),
        ('xlsx', ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'date_of_birth']),
        ('xls', ['uhl_system_number', 'nhs_number', 'family_name', 'given_name', 'gender', 'date_of_birth']),
    ],
)
def test__extract_data__missing_columns(client, faker, column_headings, extension, mock_schedule_lookup_tasks, mock_log_exception):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, extension=extension, column_headings=column_headings)
    dr = dth.get_demographics_request__data_extraction()

    extract_data(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)
    mock_log_exception.assert_not_called()

    assert len(actual.data) == 1
    assert actual.data_extracted == True
    assert actual.data_extracted_datetime is not None

    for e, a in zip(dth.get_input_details(), actual.data):
        assert e.get('uhl_system_number', '') == a.uhl_system_number
        assert e.get('nhs_number', '') == a.nhs_number
        assert e.get('family_name', '') == a.family_name
        assert e.get('given_name', '') == a.given_name
        assert e.get('gender', '') == a.gender
        assert parse_date(e.get('date_of_birth', '')) == parse_date(a.dob)
        assert e.get('postcode', '') == a.postcode

    _remove_files(dr)

def test__extract_data__columns_not_defined(client, faker, mock_schedule_lookup_tasks, mock_log_exception):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__uploaded()

    extract_data(dr.id)

    mock_schedule_lookup_tasks.assert_not_called()
    mock_log_exception.assert_called_once()

    _remove_files(dr)


def test__extract_data__already_extracted(client, faker, mock_schedule_lookup_tasks, mock_log_exception):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    extract_data(dr.id)

    mock_schedule_lookup_tasks.assert_not_called()
    mock_log_exception.assert_called_once()

    _remove_files(dr)


def test__extract_data__request_not_exists(client, faker, mock_schedule_lookup_tasks, mock_log_exception):
    extract_data(1)

    mock_schedule_lookup_tasks.assert_not_called()
    mock_log_exception.assert_called_once()


def _remove_files(dr):
    with contextlib.suppress(FileNotFoundError):
        os.remove(dr.filepath)
        os.remove(dr.result_filepath)