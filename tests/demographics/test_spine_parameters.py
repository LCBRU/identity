import contextlib
import os
from lbrc_flask.validators import parse_date
from identity.demographics import get_spine_parameters
from lbrc_flask.data_conversions import (
    convert_gender,
)
from lbrc_flask.pytest.helpers import login
from tests.demographics import (
    DemographicsTestHelper,
)


def test__get_spine_parameters__no_pmi__valid_except_nhs_number(client, faker, mock_convert_nhs_number):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, find_pre_pmi_details=False)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_nhs_number.return_value = (error_message, '')

    actual = get_spine_parameters(drd)

    mock_convert_nhs_number.assert_called_once_with(drd.nhs_number)

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == None
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'nhs_number'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__no_pmi__valid_except_gender(client, faker, mock_convert_gender):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, find_pre_pmi_details=False)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_gender.return_value = (error_message, '')

    actual = get_spine_parameters(drd)

    mock_convert_gender.assert_called_once_with(drd.gender.lower())

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == None
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'gender'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__no_pmi__valid_except_names(client, faker, mock_convert_name):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, find_pre_pmi_details=False)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_name.return_value = (error_message, '')

    actual = get_spine_parameters(drd)

    mock_convert_name.call_count = 2

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == None
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == None
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 2
    assert actual.warnings[0].scope == 'family_name'
    assert actual.warnings[0].message == error_message
    assert actual.warnings[1].scope == 'given_name'
    assert actual.warnings[1].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__no_pmi__valid_except_dob(client, faker, mock_convert_dob):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, find_pre_pmi_details=False)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_dob.return_value = (error_message, '')

    actual = get_spine_parameters(drd)

    mock_convert_dob.assert_called_once_with(drd.dob)

    assert parse_date(actual.dob) == None
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'dob'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__no_pmi__valid_except_postcode(client, faker, mock_convert_postcode):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, find_pre_pmi_details=False)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_postcode.return_value = (error_message, '')

    actual = get_spine_parameters(drd)

    mock_convert_postcode.assert_called_once_with(drd.postcode)

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == None

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'postcode'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_nhs_number(client, faker, mock_convert_nhs_number):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_nhs_number.side_effect = [(error_message, ''), (None, drd.pmi_data.nhs_number)]

    actual = get_spine_parameters(drd)

    mock_convert_nhs_number.call_count == 2

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.pmi_data.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'nhs_number'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_pmi_nhs_number(client, faker, mock_convert_nhs_number):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_nhs_number.side_effect = [(None, drd.nhs_number), (error_message, '')]

    actual = get_spine_parameters(drd)

    mock_convert_nhs_number.call_count == 2

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'pmi_nhs_number'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_gender(client, faker, mock_convert_gender):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_gender.side_effect = [(error_message, ''), (None, convert_gender(drd.pmi_data.gender)[1])]

    actual = get_spine_parameters(drd)

    mock_convert_gender.call_count == 2

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.pmi_data.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'gender'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_pmi_gender(client, faker, mock_convert_gender):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_gender.side_effect = [(None, convert_gender(drd.gender))[1], (error_message, '')]

    actual = get_spine_parameters(drd)

    mock_convert_gender.call_count == 2

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'pmi_gender'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_names(client, faker, mock_convert_name):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_name.side_effect = [
        (error_message, ''),
        (error_message, ''),
        (None, drd.pmi_data.family_name),
        (None, drd.pmi_data.given_name),
    ]

    actual = get_spine_parameters(drd)

    mock_convert_name.call_count = 4

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.pmi_data.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.pmi_data.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 2
    assert actual.warnings[0].scope == 'family_name'
    assert actual.warnings[0].message == error_message
    assert actual.warnings[1].scope == 'given_name'
    assert actual.warnings[1].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_pmi_names(client, faker, mock_convert_name):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_name.side_effect = [
        (None, drd.family_name),
        (None, drd.given_name),
        (error_message, ''),
        (error_message, ''),
    ]

    actual = get_spine_parameters(drd)

    mock_convert_name.call_count = 4

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 2
    assert actual.warnings[0].scope == 'pmi_family_name'
    assert actual.warnings[0].message == error_message
    assert actual.warnings[1].scope == 'pmi_given_name'
    assert actual.warnings[1].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_dob(client, faker, mock_convert_dob):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_dob.side_effect = [
        (error_message, None),
        (None, drd.pmi_data.date_of_birth),
    ]

    actual = get_spine_parameters(drd)

    mock_convert_dob.call_count == 2

    assert parse_date(actual.dob) == parse_date(drd.pmi_data.date_of_birth)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'dob'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_pmi_dob(client, faker, mock_convert_dob):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_dob.side_effect = [
        (None, drd.dob),
        (error_message, None),
    ]

    actual = get_spine_parameters(drd)

    mock_convert_dob.call_count == 2

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'pmi_date_of_birth'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_postcode(client, faker, mock_convert_postcode):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_postcode.side_effect = [
        (error_message, ''),
        (None, drd.pmi_data.postcode),
    ]

    actual = get_spine_parameters(drd)

    mock_convert_postcode.call_count == 2

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.pmi_data.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'postcode'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def test__get_spine_parameters__with_pmi__valid_except_pmi_postcode(client, faker, mock_convert_postcode):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()
    drd = dr.data[0]

    error_message = 'ABCDEFG'

    mock_convert_postcode.side_effect = [
        (None, drd.postcode),
        (error_message, ''),
    ]

    actual = get_spine_parameters(drd)

    mock_convert_postcode.call_count == 2

    assert parse_date(actual.dob) == parse_date(drd.dob)
    assert actual.family_name == drd.family_name
    assert actual.gender == convert_gender(drd.gender)[1]
    assert actual.given_name == drd.given_name
    assert actual.nhs_number == drd.nhs_number
    assert actual.postcode == drd.postcode

    assert len(actual.warnings) == 1
    assert actual.warnings[0].scope == 'pmi_postcode'
    assert actual.warnings[0].message == error_message

    _remove_files(dr)


def _remove_files(dr):
    with contextlib.suppress(FileNotFoundError):
        os.remove(dr.filepath)
        os.remove(dr.result_filepath)
