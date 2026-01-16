# -*- coding: utf-8 -*-

import pytest
from identity.services.pmi import (
    PmiData,
    PmiException,
    get_pmi_from_nhs_number,
    get_pmi_from_uhl_system_number,
    get_pmi,
)

def test__get_pmi_from_nhs_number__one(client, faker, mock_pmi_engine):
    expected = faker.pmi_details_cls(1)
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [expected]

    actual = get_pmi_from_nhs_number(expected.nhs_number)

    assert mock_pmi_engine.return_value.__enter__.return_value.execute.called

    assert actual.nhs_number == expected.nhs_number
    assert actual.uhl_system_number == expected.uhl_system_number
    assert actual.family_name == expected.family_name
    assert actual.given_name == expected.given_name
    assert actual.gender == expected.gender
    assert actual.date_of_birth == expected.date_of_birth
    assert actual.date_of_death == expected.date_of_death
    assert actual.postcode == expected.postcode


def test__get_pmi_from_nhs_number__none(client, faker, mock_pmi_engine):
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = []

    actual = get_pmi_from_nhs_number(faker.nhs_number())

    mock_pmi_engine.return_value.__enter__.return_value.execute.assert_called_once()

    assert actual is None


def test__get_pmi_from_nhs_number__multiple(client, faker, mock_pmi_engine):
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [faker.pmi_details(1), faker.pmi_details(2)]

    with pytest.raises(Exception):
        get_pmi_from_nhs_number(faker.nhs_number())

    assert mock_pmi_engine.return_value.__enter__.return_value.execute.called


def test__get_pmi_from_uhl_system_number__one(client, faker, mock_pmi_engine):
    expected = faker.pmi_details_cls(1)
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [faker.pmi_details_cls(1)]

    actual = get_pmi_from_uhl_system_number(expected.uhl_system_number)

    mock_pmi_engine.return_value.__enter__.return_value.execute.assert_called_once()

    assert actual.nhs_number == expected.nhs_number
    assert actual.uhl_system_number == expected.uhl_system_number
    assert actual.family_name == expected.family_name
    assert actual.given_name == expected.given_name
    assert actual.gender == expected.gender
    assert actual.date_of_birth == expected.date_of_birth
    assert actual.date_of_death == expected.date_of_death
    assert actual.postcode == expected.postcode


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


def test__get_pmi__nhs_found(client, faker, mock_pmi_engine):
    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[faker.pmi_details_cls(1)], [faker.pmi_details_cls(1)], []]

    actual = get_pmi(nhs_number=expected.nhs_number, uhl_system_number=expected.uhl_system_number)

    assert actual == expected


def test__get_pmi__uhl_found(client, faker, mock_pmi_engine):
    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[], [faker.pmi_details_cls(1)]]

    actual = get_pmi(nhs_number=expected.nhs_number, uhl_system_number=expected.uhl_system_number)

    assert actual == expected


def test__get_pmi__neither_found(client, faker, mock_pmi_engine):
    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[], [], []]

    actual = get_pmi(nhs_number=expected.nhs_number, uhl_system_number=expected.uhl_system_number)

    assert actual is None


def test__get_pmi__nhs_multiple(client, faker, mock_pmi_engine):
    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[faker.pmi_details_cls(1), faker.pmi_details_cls(2)], []]

    with pytest.raises(Exception):
        get_pmi(nhs_number=expected.nhs_number, uhl_system_number=expected.uhl_system_number)


def test__get_pmi__uhl_multiple(client, faker, mock_pmi_engine):
    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[], [faker.pmi_details_cls(1), faker.pmi_details_cls(2)]]

    with pytest.raises(Exception):
        get_pmi(nhs_number=expected.nhs_number, uhl_system_number=expected.uhl_system_number)


def test__get_pmi__differ(client, faker, mock_pmi_engine):
    expected = PmiData(**faker.pmi_details(1))
    mock_pmi_engine.return_value.__enter__.return_value.execute.return_value.fetchall.side_effect = [[faker.pmi_details_cls(1)], [faker.pmi_details_cls(2)], [faker.pmi_details_cls(3)]]

    with pytest.raises(PmiException):
        get_pmi(nhs_number=expected.nhs_number, uhl_system_number=expected.uhl_system_number)
