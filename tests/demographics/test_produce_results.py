import contextlib
import pytest
import os
from unittest.mock import patch
from identity.demographics import produce_demographics_result
from identity.demographics.model import DemographicsRequestCsv, DemographicsRequest
from lbrc_flask.validators import parse_date
from lbrc_flask.pytest.helpers import login
from tests.demographics import DemographicsTestHelper


@pytest.yield_fixture(scope="function")
def mock_email(app):
    with patch('identity.demographics.email') as mock_email:
        yield mock_email


@pytest.mark.parametrize(
    "row_count, extension",
    [
        (0, 'csv'),
        (1, 'csv'),
        (1000, 'csv'),
        (0, 'xlsx'),
        (1, 'xlsx'),
        (1000, 'xlsx'),
        (0, 'xls'),
        (1, 'xls'),
        (1000, 'xls'),
    ],
)
def test__produce_demographics_result(client, faker, mock_email, row_count, extension):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=row_count, extension=extension, include_data_errors=True)
    dr = dth.get_demographics_request__create_results()

    produce_demographics_result(dr.id)

    mock_email.assert_called_once()

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.result_created_datetime is not None
    assert dr.result_created
    assert os.path.isfile(dr.result_filepath)

    for row, expected in zip(dr.iter_result_rows(), dth._person_details):
        assert row['spine_title'] == expected['title']
        assert row['spine_forename'] == expected['given_name']
        assert row['spine_middlenames'] == expected['middle_name']
        assert row['spine_lastname'] == expected['family_name']
        assert row['spine_postcode'] == expected['postcode']
        assert row['spine_address'] == expected['address']
        assert parse_date(row['spine_date_of_birth']) == parse_date(expected["date_of_birth"])
        assert parse_date(row['spine_date_of_death']) == parse_date(expected["date_of_death"])
        assert (row['spine_is_deceased'] == 'True') == expected['is_deceased']
        assert row['spine_current_gp_practice_code'] == expected['current_gp_practice_code']
        assert row['spine_message'] or '' == expected['expected_message']

        assert row['pmi_nhs_number'] == expected['nhs_number']
        assert row['pmi_uhl_system_number'] == expected['uhl_system_number']
        assert row['pmi_family_name'] == expected['family_name']
        assert row['pmi_given_name'] == expected['given_name']
        assert row['pmi_gender'] == expected['gender']
        assert parse_date(row['pmi_dob']) == parse_date(expected['date_of_birth'])
        assert parse_date(row['pmi_date_of_death']) == parse_date(expected["date_of_death"])
        assert row['pmi_postcode'] == expected['postcode']

    _remove_files(dr)


def _remove_files(dr):
    with contextlib.suppress(FileNotFoundError):
        os.remove(dr.filepath)
        os.remove(dr.result_filepath)
