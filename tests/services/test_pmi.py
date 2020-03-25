# -*- coding: utf-8 -*-

import pytest
import datetime
from dateutil.parser import parse
from identity.services.pmi import (
    PmiData,
    get_pmi_from_nhs_number,
    get_pmi_from_uhl_system_number,
)

def test__get_pmi_from_nhs_number__one(client, faker, mock_pmi_engine):
    expected = faker.pmi_details(1)
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [expected]

    actual = get_pmi_from_nhs_number(expected['nhs_number'])

    mock_pmi_engine.return_value.__enter__.return_value.execute.assert_called_once()

    assert actual.nhs_number == expected['nhs_number']
    assert actual.uhl_system_number == expected['uhl_system_number']
    assert actual.family_name == expected['family_name']
    assert actual.given_name == expected['given_name']
    assert actual.gender == expected['gender']
    assert actual.date_of_birth == expected['date_of_birth']
    assert actual.date_of_death == expected['date_of_death']
    assert actual.postcode == expected['postcode']


def test__get_pmi_from_nhs_number__none(client, faker, mock_pmi_engine):
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = []

    actual = get_pmi_from_nhs_number(faker.nhs_number())

    mock_pmi_engine.return_value.__enter__.return_value.execute.assert_called_once()

    assert actual is None


def test__get_pmi_from_nhs_number__multiple(client, faker, mock_pmi_engine):
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [faker.pmi_details(1), faker.pmi_details(2)]

    with pytest.raises(Exception):
        get_pmi_from_nhs_number(faker.nhs_number())

    mock_pmi_engine.return_value.__enter__.return_value.execute.assert_called_once()


def test__get_pmi_from_uhl_system_number__one(client, faker, mock_pmi_engine):
    expected = faker.pmi_details(1)
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [expected]

    actual = get_pmi_from_uhl_system_number(expected['uhl_system_number'])

    mock_pmi_engine.return_value.__enter__.return_value.execute.assert_called_once()

    assert actual.nhs_number == expected['nhs_number']
    assert actual.uhl_system_number == expected['uhl_system_number']
    assert actual.family_name == expected['family_name']
    assert actual.given_name == expected['given_name']
    assert actual.gender == expected['gender']
    assert actual.date_of_birth == expected['date_of_birth']
    assert actual.date_of_death == expected['date_of_death']
    assert actual.postcode == expected['postcode']


def test__get_pmi_from_uhl_system_number__none(client, faker, mock_pmi_engine):
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = []

    actual = get_pmi_from_uhl_system_number(faker.uhl_system_number())

    mock_pmi_engine.return_value.__enter__.return_value.execute.assert_called_once()

    assert actual is None


def test__get_pmi_from_uhl_system_number__multiple(client, faker, mock_pmi_engine):
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [faker.pmi_details(1), faker.pmi_details(2)]

    with pytest.raises(Exception):
        get_pmi_from_uhl_system_number(faker.uhl_system_number())

    mock_pmi_engine.return_value.__enter__.return_value.execute.assert_called_once()
