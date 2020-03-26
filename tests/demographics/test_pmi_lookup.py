# -*- coding: utf-8 -*-

import pytest
import datetime
from unittest.mock import patch
from dateutil.parser import parse
from identity.demographics.model import (
    DemographicsRequest,
)
from identity.demographics import extract_pre_pmi_details, extract_post_pmi_details
from identity.services.pmi import PmiData, PmiException
from identity.database import db
from tests import login
from tests.demographics import (
    DemographicsTestHelper
)


@pytest.yield_fixture(scope="function")
def mock_pmi_details(app):
    with patch('identity.demographics.get_pmi') as mock_pmi_details:
        yield mock_pmi_details


# Pre-Lookup

def test__extract_pre_pmi_details__no_data(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__uploaded()

    extract_pre_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_pre_completed_datetime is not None
    

@pytest.mark.parametrize(
    "row_count",
    [
        (1),
        (10),
    ],
)
def test__extract_pre_pmi_details__first_processed(client, faker, mock_pmi_details, row_count):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=row_count)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_details.return_value = expected

    extract_pre_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert expected == actual.data[0].pmi_data
    assert len(actual.data[0].messages) == 0


def test__extract_pre_pmi_details__next_processed(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=2)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    dr.data[0].pmi_pre_processed_datetime = datetime.datetime.utcnow()
    db.session.add(dr.data[0])
    db.session.commit()

    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_details.return_value = expected

    extract_pre_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 2
    assert expected == actual.data[1].pmi_data
    assert len(actual.data[0].messages) == 0


def test__extract_pre_pmi_details__last_processed(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    dr.data[0].pmi_pre_processed_datetime = datetime.datetime.utcnow()
    db.session.add(dr.data[0])
    db.session.commit()

    extract_pre_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_pre_completed_datetime is not None
    assert len(actual.data[0].messages) == 0


def test__extract_pre_pmi_details__invalid_nhs_number(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    dr.data[0].nhs_number = faker.invalid_nhs_number()
    db.session.add(dr.data[0])
    db.session.commit()

    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_details.return_value = expected

    extract_pre_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert expected == actual.data[0].pmi_data
    assert len(actual.data[0].messages) == 1

    m = actual.data[0].messages[0]
    assert m.type == 'warning'
    assert m.source == 'pmi_details'
    assert m.scope == 'nhs_number'
    assert m.message == f'Invalid format {faker.invalid_nhs_number()}'


def test__extract_pre_pmi_details__invalid_uhl_system_number(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    dr.data[0].uhl_system_number = faker.invalid_uhl_system_number()
    db.session.add(dr.data[0])
    db.session.commit()

    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_details.return_value = expected

    extract_pre_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert expected == actual.data[0].pmi_data
    assert len(actual.data[0].messages) == 1

    m = actual.data[0].messages[0]
    assert m.type == 'warning'
    assert m.source == 'pmi_details'
    assert m.scope == 'uhl_system_number'
    assert m.message == f'Invalid format {faker.invalid_uhl_system_number()}'


def test__extract_pre_pmi_details__pmi_not_found(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    mock_pmi_details.return_value = None

    extract_pre_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert actual.data[0].pmi_data is None
    assert len(actual.data[0].messages) == 0


def test__extract_pre_pmi_details__pmi_exception(client, faker, mock_pmi_details):
    ERROR_MESSAGE = 'An Exception'

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    mock_pmi_details.side_effect = PmiException(ERROR_MESSAGE)

    extract_pre_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_pre_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_pre_processed_datetime is not None) == 1
    assert actual.data[0].pmi_data is None
    assert len(actual.data[0].messages) == 1

    m = actual.data[0].messages[0]
    assert m.type == 'error'
    assert m.source == 'pmi_details'
    assert m.scope == 'pmi_details'
    assert m.message == ERROR_MESSAGE


# Post-Lookup

def test__extract_post_pmi_details__no_data(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__uploaded()

    extract_post_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_post_completed_datetime is not None
    

@pytest.mark.parametrize(
    "row_count",
    [
        (1),
        (10),
    ],
)
def test__extract_post_pmi_details__first_processed(client, faker, mock_pmi_details, row_count):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=row_count)
    dr = dth.get_demographics_request__post_pmi_lookup()

    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_details.return_value = expected

    extract_post_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_post_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_post_processed_datetime is not None) == 1
    assert expected == actual.data[0].pmi_data
    assert len(actual.data[0].messages) == 0


def test__extract_post_pmi_details__next_processed(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=2)
    dr = dth.get_demographics_request__post_pmi_lookup()

    dr.data[0].pmi_post_processed_datetime = datetime.datetime.utcnow()
    db.session.add(dr.data[0])
    db.session.commit()

    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_details.return_value = expected

    extract_post_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_post_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_post_processed_datetime is not None) == 2
    assert expected == actual.data[1].pmi_data
    assert len(actual.data[0].messages) == 0


def test__extract_post_pmi_details__last_processed(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__post_pmi_lookup()

    dr.data[0].pmi_post_processed_datetime = datetime.datetime.utcnow()
    db.session.add(dr.data[0])
    db.session.commit()

    extract_post_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_post_completed_datetime is not None
    assert len(actual.data[0].messages) == 0


def test__extract_post_pmi_details__invalid_nhs_number(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__post_pmi_lookup()

    dr.data[0].nhs_number = faker.invalid_nhs_number()
    db.session.add(dr.data[0])
    db.session.commit()

    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_details.return_value = expected

    extract_post_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_post_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_post_processed_datetime is not None) == 1
    assert expected == actual.data[0].pmi_data
    assert len(actual.data[0].messages) == 1

    m = actual.data[0].messages[0]
    assert m.type == 'warning'
    assert m.source == 'pmi_details'
    assert m.scope == 'nhs_number'
    assert m.message == f'Invalid format {faker.invalid_nhs_number()}'


def test__extract_post_pmi_details__invalid_uhl_system_number(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__post_pmi_lookup()

    dr.data[0].uhl_system_number = faker.invalid_uhl_system_number()
    db.session.add(dr.data[0])
    db.session.commit()

    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_details.return_value = expected

    extract_post_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_post_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_post_processed_datetime is not None) == 1
    assert expected == actual.data[0].pmi_data
    assert len(actual.data[0].messages) == 1

    m = actual.data[0].messages[0]
    assert m.type == 'warning'
    assert m.source == 'pmi_details'
    assert m.scope == 'uhl_system_number'
    assert m.message == f'Invalid format {faker.invalid_uhl_system_number()}'


def test__extract_post_pmi_details__pmi_not_found(client, faker, mock_pmi_details):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__post_pmi_lookup()

    mock_pmi_details.return_value = None

    extract_post_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_post_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_post_processed_datetime is not None) == 1
    assert actual.data[0].pmi_data is None
    assert len(actual.data[0].messages) == 0


def test__extract_post_pmi_details__pmi_exception(client, faker, mock_pmi_details):
    ERROR_MESSAGE = 'An Exception'

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__post_pmi_lookup()

    mock_pmi_details.side_effect = PmiException(ERROR_MESSAGE)

    extract_post_pmi_details(dr.id)

    actual = DemographicsRequest.query.get(dr.id)

    assert actual.pmi_data_post_completed_datetime is None
    assert sum(1 for d in actual.data if d.pmi_post_processed_datetime is not None) == 1
    assert actual.data[0].pmi_data is None
    assert len(actual.data[0].messages) == 1

    m = actual.data[0].messages[0]
    assert m.type == 'error'
    assert m.source == 'pmi_details'
    assert m.scope == 'pmi_details'
    assert m.message == ERROR_MESSAGE
