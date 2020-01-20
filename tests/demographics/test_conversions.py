# -*- coding: utf-8 -*-

import pytest
import datetime
from identity.demographics import (
    convert_dob,
)


@pytest.mark.parametrize(
    "date_value, has_error, expected",
    [
        ('1944-12-19 00:00:00', False, '19441219'),
        ('1944-12-19', False, '19441219'),
        ('01/02/1923', False, '19230201'),
        ('31/01/1923', False, '19230131'),
        ('32/01/1923', True, ''),
        ('29/02/1996', False, '19960229'),
        ('12/06/1948', False, '19480612'),
        ('1948-06-12 00:00:00', False, '19480612'),
        ('1948-06-12T00:00:00', False, '19480612'),
        ('1948-06-12 00:00:00.0', False, '19480612'),
        ('1948-06-12T00:00:00.00000000', False, '19480612'),
        ('1997-07-16T19:20:30+01:00', False, '19970716'),
        ('1997-07-16T19:20:30-01:00', False, '19970716'),
        ('1997-07-16T19:20:30Z', False, '19970716'),
        ('29/02/1997', True, ''),
        ('29-02-1996', False, '19960229'),
        ('29 02 1996', False, '19960229'),
        ('29 Feb 1996', False, '19960229'),
        ('29 February 1996', False, '19960229'),
        (datetime.datetime(1996, 2, 29), False, '19960229'),
        ('19/12/1944', False, '19441219'),
        ('19440103', False, '19440103'),
    ],
)
def test__convert_dob__parsing(client, date_value, has_error, expected):
    error, converted_date = convert_dob(date_value)

    assert (error is None) != has_error
    assert converted_date == expected