import contextlib
import os
import pytest
from unittest.mock import MagicMock
from identity.services.validators import parse_date
from identity.demographics import (
    spine_lookup,
    SpineParameters,
    SmspException,
)
from identity.demographics.smsp import (
    SmspNoMatchException,
    SmspMultipleMatchesException,
    SmspNhsNumberSupersededException,
    SmspNhsNumberInvalidException,
    SmspNhsNumberNotVerifiedException,
    SmspNhsNumberNotNewStyleException,
)
from tests import login
from tests.demographics import (
    DemographicsTestHelper,
)


spine_response_full = MagicMock(
    title='Ms',
    forename='Janet',
    middlenames='Sarah',
    lastname='Smyth',
    postcode='LE8 10TY',
    address='1 The Road, Leicester',
    date_of_birth='01-Jan-1970',
    date_of_death='31-Dec-2010',
    is_deceased=True,
    current_gp_practice_code='G98764',
    sex='Female',
    nhs_number='3333333333',
)

@pytest.mark.parametrize(
    "warning_count",
    [
        (0),
        (1),
        (10),
    ],
)
def test__spine_lookup__nhs_number(client, faker, mock_get_spine_parameters, mock_get_demographics_from_nhs_number, mock_get_demographics_from_search, warning_count):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    params = SpineParameters()
    params.nhs_number=drd.nhs_number
    params.dob=drd.dob
    params.family_name=drd.family_name
    params.given_name=drd.given_name
    params.gender=drd.gender
    params.postcode=drd.postcode

    for i in range(warning_count):
        params.add_warning(
            scope=f'scope {i}',
            message=f'message {i}',
        )

    mock_get_spine_parameters.return_value = params
    mock_get_demographics_from_nhs_number.return_value = spine_response_full

    spine_lookup(drd)

    mock_get_demographics_from_nhs_number.assert_called_once_with(
        nhs_number=params.nhs_number,
        dob=params.dob,
    )
    mock_get_demographics_from_search.assert_not_called()

    assert drd.response is not None
    assert drd.response.nhs_number == spine_response_full.nhs_number
    assert drd.response.title == spine_response_full.title
    assert drd.response.forename == spine_response_full.forename
    assert drd.response.middlenames == spine_response_full.middlenames
    assert drd.response.lastname == spine_response_full.lastname
    assert drd.response.sex == spine_response_full.sex
    assert drd.response.postcode == spine_response_full.postcode
    assert drd.response.address == spine_response_full.address
    assert parse_date(drd.response.date_of_birth) == parse_date(spine_response_full.date_of_birth)
    assert parse_date(drd.response.date_of_death) == parse_date(spine_response_full.date_of_death)
    assert drd.response.is_deceased == spine_response_full.is_deceased
    assert drd.response.current_gp_practice_code == spine_response_full.current_gp_practice_code

    assert len(drd.messages) == warning_count

    for i, w in enumerate(drd.messages):
        assert w.type == 'warning'
        assert w.source == 'validation'
        assert w.scope == f'scope {i}'
        assert w.message == f'message {i}'

    _remove_files(dr)


@pytest.mark.parametrize(
    "warning_count",
    [
        (0),
        (1),
        (10),
    ],
)
def test__spine_lookup__search(client, faker, mock_get_spine_parameters, mock_get_demographics_from_nhs_number, mock_get_demographics_from_search, warning_count):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    params = SpineParameters()
    params.nhs_number=''
    params.dob=drd.dob
    params.family_name=drd.family_name
    params.given_name=drd.given_name
    params.gender=drd.gender
    params.postcode=drd.postcode

    for i in range(warning_count):
        params.add_warning(
            scope=f'scope {i}',
            message=f'message {i}',
        )

    mock_get_spine_parameters.return_value = params
    mock_get_demographics_from_search.return_value = spine_response_full

    spine_lookup(drd)

    mock_get_demographics_from_search.assert_called_once_with(
        family_name=params.family_name,
        given_name=params.given_name,
        gender=params.gender,
        dob=params.dob,
        postcode=params.postcode,
    )
    mock_get_demographics_from_nhs_number.assert_not_called()

    assert drd.response is not None
    assert drd.response.nhs_number == spine_response_full.nhs_number
    assert drd.response.title == spine_response_full.title
    assert drd.response.forename == spine_response_full.forename
    assert drd.response.middlenames == spine_response_full.middlenames
    assert drd.response.lastname == spine_response_full.lastname
    assert drd.response.sex == spine_response_full.sex
    assert drd.response.postcode == spine_response_full.postcode
    assert drd.response.address == spine_response_full.address
    assert parse_date(drd.response.date_of_birth) == parse_date(spine_response_full.date_of_birth)
    assert parse_date(drd.response.date_of_death) == parse_date(spine_response_full.date_of_death)
    assert drd.response.is_deceased == spine_response_full.is_deceased
    assert drd.response.current_gp_practice_code == spine_response_full.current_gp_practice_code

    assert len(drd.messages) == warning_count

    for i, w in enumerate(drd.messages):
        assert w.type == 'warning'
        assert w.source == 'validation'
        assert w.scope == f'scope {i}'
        assert w.message == f'message {i}'

    _remove_files(dr)


def test__spine_lookup__search_no_gender(client, faker, mock_get_spine_parameters, mock_get_demographics_from_nhs_number, mock_get_demographics_from_search):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    params = SpineParameters()
    params.nhs_number=''
    params.dob=drd.dob
    params.family_name=drd.family_name
    params.given_name=drd.given_name
    params.gender=None
    params.postcode=drd.postcode

    mock_get_spine_parameters.return_value = params
    mock_get_demographics_from_search.return_value = spine_response_full

    spine_lookup(drd)

    mock_get_demographics_from_search.assert_not_called()
    mock_get_demographics_from_nhs_number.assert_not_called()

    _remove_files(dr)


def test__spine_lookup__no_parameters(client, faker, mock_get_spine_parameters, mock_get_demographics_from_nhs_number, mock_get_demographics_from_search):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    params = SpineParameters()

    mock_get_spine_parameters.return_value = params
    mock_get_demographics_from_search.return_value = spine_response_full

    spine_lookup(drd)

    mock_get_demographics_from_search.assert_not_called()
    mock_get_demographics_from_nhs_number.assert_not_called()

    assert drd.response is None

    assert len(drd.messages) == 1

    assert drd.messages[0].type == 'error'
    assert drd.messages[0].source == 'validation'
    assert drd.messages[0].scope == 'request'
    assert drd.messages[0].message == 'Not enough values to perform Spine lookup'

    _remove_files(dr)


@pytest.mark.parametrize(
    "exception_class,message_type",
    [
        (SmspNoMatchException, 'error'),
        (SmspMultipleMatchesException, 'error'),
        (SmspNhsNumberSupersededException, 'error'),
        (SmspNhsNumberInvalidException, 'error'),
        (SmspNhsNumberNotVerifiedException, 'error'),
        (SmspNhsNumberNotNewStyleException, 'error'),
        (SmspException, 'error'),
        (Exception, 'unknown error'),
    ],
)
def test__spine_lookup__spine_exception(client, faker, mock_get_spine_parameters, mock_get_demographics_from_nhs_number, mock_get_demographics_from_search, exception_class, message_type):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    params = SpineParameters()
    params.nhs_number=drd.nhs_number
    params.dob=drd.dob

    mock_get_spine_parameters.return_value = params
    mock_get_demographics_from_nhs_number.side_effect = exception_class

    spine_lookup(drd)

    assert drd.response is None

    assert len(drd.messages) == 1

    assert drd.messages[0].type == message_type
    assert drd.messages[0].source == 'spine'
    assert drd.messages[0].scope == 'request'

    _remove_files(dr)


def _remove_files(dr):
    with contextlib.suppress(FileNotFoundError):
        os.remove(dr.filepath)
        os.remove(dr.result_filepath)
