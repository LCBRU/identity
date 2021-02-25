import pytest
from unittest.mock import patch


@pytest.yield_fixture(scope="function")
def mock_pmi_engine(app):
    with patch('identity.services.pmi.pmi_engine') as mock_engine:
        yield mock_engine


@pytest.yield_fixture(scope="function")
def mock_schedule_lookup_tasks(app):
    with patch('identity.demographics.schedule_lookup_tasks') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_pmi_details(app):
    with patch('identity.demographics.get_pmi') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_spine_lookup(app):
    with patch('identity.demographics.spine_lookup') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_log_exception(app):
    with patch('identity.demographics.log_exception') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_get_demographics_from_search(app):
    with patch('identity.demographics.get_demographics_from_search') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_get_demographics_from_nhs_number(app):
    with patch('identity.demographics.get_demographics_from_nhs_number') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_convert_nhs_number(app):
    with patch('identity.demographics.convert_nhs_number') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_convert_gender(app):
    with patch('identity.demographics.convert_gender') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_convert_name(app):
    with patch('identity.demographics.convert_name') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_convert_dob(app):
    with patch('identity.demographics.convert_dob') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_convert_postcode(app):
    with patch('identity.demographics.convert_postcode') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_get_spine_parameters(app):
    with patch('identity.demographics.get_spine_parameters') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_process_demographics_request_data(app):
    with patch('identity.demographics.process_demographics_request_data') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_extract_data(app):
    with patch('identity.demographics.extract_data') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_produce_demographics_result(app):
    with patch('identity.demographics.produce_demographics_result') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_extract_pre_pmi_details(app):
    with patch('identity.demographics.extract_pre_pmi_details') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_extract_post_pmi_details(app):
    with patch('identity.demographics.extract_post_pmi_details') as mock:
        yield mock
