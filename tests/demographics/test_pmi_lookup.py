from typing import Optional

import pytest
import datetime
from identity.demographics.model import DemographicsRequest
from identity.demographics import extract_pre_pmi_details
from identity.services.pmi import PmiException
from lbrc_flask.database import db
from lbrc_flask.pytest.helpers import login
from tests.demographics import DemographicsTestHelper
from lbrc_flask.database import db

# Pre-Lookup

def test__extract_pre_pmi_details__no_data(client, faker, mock_pmi_details, mock_schedule_lookup_tasks):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__uploaded()

    extract_pre_pmi_details(dr.id)

    actual: Optional[DemographicsRequest] = db.session.get(DemographicsRequest, dr.id)

    assert actual is not None
    assert actual.pmi_data_pre_completed_datetime is not None
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)
    

@pytest.mark.parametrize(
    "row_count",
    [
        (1),
        (10),
    ],
)
def test__extract_pre_pmi_details__first_processed(client, faker, mock_pmi_details, row_count, mock_schedule_lookup_tasks):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=row_count)
    dr = dth.get_demographics_request__request_data_extracted()

    expected = faker.pmi_data().get(save=False)
    mock_pmi_details.return_value = expected

    extract_pre_pmi_details(dr.id)

    actual: Optional[DemographicsRequest] = db.session.get(DemographicsRequest, dr.id)

    assert actual is not None
    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert expected == actual.data[0].pmi_data
    assert len(actual.data[0].messages) == 0
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)


def test__extract_pre_pmi_details__next_processed(client, faker, mock_pmi_details, mock_schedule_lookup_tasks):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=2)
    dr = dth.get_demographics_request__request_data_extracted()

    dr.data[0].pmi_pre_processed_datetime = datetime.datetime.now(datetime.UTC)
    db.session.add(dr.data[0])
    db.session.commit()

    expected = faker.pmi_data().get(save=False)
    mock_pmi_details.return_value = expected

    extract_pre_pmi_details(dr.id)

    actual: Optional[DemographicsRequest] = db.session.get(DemographicsRequest, dr.id)

    assert actual is not None
    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 2
    assert expected == actual.data[1].pmi_data
    assert len(actual.data[0].messages) == 0
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)


def test__extract_pre_pmi_details__last_processed(client, faker, mock_pmi_details, mock_schedule_lookup_tasks):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__request_data_extracted()

    dr.data[0].pmi_pre_processed_datetime = datetime.datetime.now(datetime.UTC)
    db.session.add(dr.data[0])
    db.session.commit()

    extract_pre_pmi_details(dr.id)

    actual: Optional[DemographicsRequest] = db.session.get(DemographicsRequest, dr.id)

    assert actual is not None
    assert actual.pmi_data_pre_completed_datetime is not None
    assert len(actual.data[0].messages) == 0
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)


def test__extract_pre_pmi_details__invalid_nhs_number(client, faker, mock_pmi_details, mock_schedule_lookup_tasks):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__request_data_extracted()

    dr.data[0].nhs_number = faker.invalid_nhs_number()
    db.session.add(dr.data[0])
    db.session.commit()

    expected = faker.pmi_data().get(save=False)
    mock_pmi_details.return_value = expected

    extract_pre_pmi_details(dr.id)

    actual: Optional[DemographicsRequest] = db.session.get(DemographicsRequest, dr.id)

    assert actual is not None
    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert expected == actual.data[0].pmi_data
    assert len(actual.data[0].messages) == 1

    m = actual.data[0].messages[0]
    assert m.type == 'warning'
    assert m.source == 'pmi_details'
    assert m.scope == 'nhs_number'
    assert m.message == f'Invalid format {faker.invalid_nhs_number()}'
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)


def test__extract_pre_pmi_details__invalid_uhl_system_number(client, faker, mock_pmi_details, mock_schedule_lookup_tasks):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__request_data_extracted()

    dr.data[0].uhl_system_number = faker.invalid_uhl_system_number()
    db.session.add(dr.data[0])
    db.session.commit()

    expected = faker.pmi_data().get(save=False)
    mock_pmi_details.return_value = expected

    extract_pre_pmi_details(dr.id)

    actual: Optional[DemographicsRequest] = db.session.get(DemographicsRequest, dr.id)

    assert actual is not None
    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert expected == actual.data[0].pmi_data
    assert len(actual.data[0].messages) == 1

    m = actual.data[0].messages[0]
    assert m.type == 'warning'
    assert m.source == 'pmi_details'
    assert m.scope == 'uhl_system_number'
    assert m.message == f'Invalid format {faker.invalid_uhl_system_number()}'
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)


def test__extract_pre_pmi_details__pmi_not_found(client, faker, mock_pmi_details, mock_schedule_lookup_tasks):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__request_data_extracted()

    mock_pmi_details.return_value = None

    extract_pre_pmi_details(dr.id)

    actual: Optional[DemographicsRequest] = db.session.get(DemographicsRequest, dr.id)

    assert actual is not None
    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert actual.data[0].pmi_data is None
    assert len(actual.data[0].messages) == 0
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)


def test__extract_pre_pmi_details__pmi_exception(client, faker, mock_pmi_details, mock_schedule_lookup_tasks):
    ERROR_MESSAGE = 'An Exception'

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__request_data_extracted()

    mock_pmi_details.side_effect = PmiException(ERROR_MESSAGE)

    extract_pre_pmi_details(dr.id)

    actual: Optional[DemographicsRequest] = db.session.get(DemographicsRequest, dr.id)

    assert actual is not None
    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert actual.data[0].pmi_data is None
    assert len(actual.data[0].messages) == 1

    m = actual.data[0].messages[0]
    assert m.type == 'error'
    assert m.source == 'pmi_details'
    assert m.scope == 'pmi_details'
    assert m.message == ERROR_MESSAGE
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)
