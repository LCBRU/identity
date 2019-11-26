# -*- coding: utf-8 -*-

import pytest
import shutil
import datetime
from unittest.mock import patch
from flask import current_app
from identity.database import db
from identity.demographics import (
    extract_data,
    schedule_lookup_tasks,
    produce_demographics_result,
)
from identity.demographics.model import (
    DemographicsRequest,
    DemographicsRequestData,
    DemographicsRequestDataMessage,
)
from identity.demographics.smsp import (
    SMSP_SEX_FEMALE,
    SMSP_SEX_MALE,
    SmspNoMatchException,
    SmspMultipleMatchesException,
    SmspNhsNumberSupersededException,
    SmspNhsNumberInvalidException,
    SmspNhsNumberNotVerifiedException,
    SmspNhsNumberNotNewStyleException,
)
from tests import login
from tests.demographics import (
    do_create_request,
    do_define_columns_post,
    do_submit,
    do_extract_data,
    do_upload_data,
    do_upload_data_and_extract,
)

@pytest.fixture(autouse=True)
def cleanup_files(client):
    yield

    shutil.rmtree(
        current_app.config["FILE_UPLOAD_DIRECTORY"],
        ignore_errors=True,
    )


def test__schedule_lookup_tasks__schedule(client, faker):
    dr = do_upload_data(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    with patch('identity.demographics.process_demographics_request_data') as mock_process_demographics_request_data, \
        patch('identity.demographics.email') as mock_email, \
        patch('identity.demographics.log_exception') as mock_log_exception, \
        patch('identity.demographics.extract_data') as mock_extract_data, \
        patch('identity.demographics.produce_demographics_result') as mock_produce_demographics_result:

        schedule_lookup_tasks(dr.id)

        mock_extract_data.delay.assert_called_once_with(dr.id)
        mock_process_demographics_request_data.delay.assert_not_called()
        mock_email.assert_not_called()
        mock_log_exception.assert_not_called()
        mock_produce_demographics_result.delay.assert_not_called()


def test__schedule_lookup_tasks__data_extracted(client, faker):
    drd = do_upload_data_and_extract(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])
    dr = drd.demographics_request

    with patch('identity.demographics.process_demographics_request_data') as mock_process_demographics_request_data, \
        patch('identity.demographics.email') as mock_email, \
        patch('identity.demographics.log_exception') as mock_log_exception, \
        patch('identity.demographics.produce_demographics_result') as mock_produce_demographics_result:

        schedule_lookup_tasks(dr.id)

        mock_process_demographics_request_data.delay.assert_called_once_with(
            data_id=drd.id,
            request_id=dr.id,
        )
        mock_email.assert_not_called()
        mock_log_exception.assert_not_called()
        mock_produce_demographics_result.delay.assert_not_called()


def test__schedule_lookup_tasks__end_lookup(client, faker):
    user = login(client, faker)

    dr = do_upload_data(client, faker, None)
    do_extract_data(dr.id)

    with patch('identity.demographics.process_demographics_request_data') as mock_process_demographics_request_data, \
        patch('identity.demographics.email') as mock_email, \
        patch('identity.demographics.log_exception') as mock_log_exception, \
        patch('identity.demographics.produce_demographics_result') as mock_produce_demographics_result:

        schedule_lookup_tasks(dr.id)

        mock_process_demographics_request_data.delay.assert_not_called()
        mock_email.assert_not_called()
        mock_log_exception.assert_not_called()
        mock_produce_demographics_result.delay.assert_called_once_with(dr.id)

        new_dr = DemographicsRequest.query.get(dr.id)
        assert new_dr.lookup_completed
        assert new_dr.lookup_completed_datetime is not None


def test__schedule_lookup_tasks__lookup_completed(client, faker):
    drd = do_upload_data_and_extract(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])
    dr = drd.demographics_request

    dr.lookup_completed_datetime = datetime.datetime.utcnow()
    db.session.add(dr)
    db.session.commit()

    with patch('identity.demographics.process_demographics_request_data') as mock_process_demographics_request_data, \
        patch('identity.demographics.email') as mock_email, \
        patch('identity.demographics.log_exception') as mock_log_exception, \
        patch('identity.demographics.produce_demographics_result') as mock_produce_demographics_result:

        schedule_lookup_tasks(dr.id)

        assert mock_process_demographics_request_data.delay.called
        mock_email.assert_not_called()
        mock_log_exception.assert_not_called()
        mock_produce_demographics_result.delay.assert_not_called()


def test__schedule_lookup_tasks__data_request_not_found(client, faker):
    with patch('identity.demographics.process_demographics_request_data') as mock_process_demographics_request_data, \
        patch('identity.demographics.email') as mock_email, \
        patch('identity.demographics.log_exception') as mock_log_exception, \
        patch('identity.demographics.produce_demographics_result') as mock_produce_demographics_result:

        schedule_lookup_tasks(76573)

        mock_process_demographics_request_data.delay.assert_not_called()
        mock_email.assert_not_called()
        assert mock_log_exception.called
        mock_produce_demographics_result.delay.assert_not_called()


def test__schedule_lookup_tasks__exception(client, faker):
    drd = do_upload_data_and_extract(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])
    dr = drd.demographics_request

    with patch('identity.demographics.process_demographics_request_data') as mock_process_demographics_request_data, \
        patch('identity.demographics.email') as mock_email, \
        patch('identity.demographics.log_exception') as mock_log_exception, \
        patch('identity.demographics.produce_demographics_result') as mock_produce_demographics_result:

        e = Exception()

        mock_process_demographics_request_data.delay.side_effect = e

        schedule_lookup_tasks(dr.id)

        mock_process_demographics_request_data.delay.assert_called_once_with(
            data_id=drd.id,
            request_id=dr.id,
        )
        mock_email.assert_not_called()
        mock_log_exception.assert_called_once_with(e)
        mock_produce_demographics_result.delay.assert_not_called()


def test__schedule_lookup_tasks__deleted(client, faker):
    dr = do_upload_data(client, faker, ['', 'Smith', 'Jane', 'Female', '01-Jan-1970', 'LE10 8HG'])

    dr.deleted_datetime = datetime.datetime.utcnow()
    db.session.add(dr)
    db.session.commit()

    with patch('identity.demographics.process_demographics_request_data') as mock_process_demographics_request_data, \
        patch('identity.demographics.email') as mock_email, \
        patch('identity.demographics.log_exception') as mock_log_exception, \
        patch('identity.demographics.produce_demographics_result') as mock_produce_demographics_result:

        schedule_lookup_tasks(dr.id)

        mock_process_demographics_request_data.delay.assert_not_called()
        mock_email.assert_not_called()
        mock_log_exception.assert_not_called()
        mock_produce_demographics_result.delay.assert_not_called()


def test__schedule_lookup_tasks__result_created(client, faker):
    headers = ['nhs_number', 'family_name', 'given_name', 'gender', 'dob', 'postcode']

    dr = do_upload_data(client, faker, None)
    do_extract_data(dr.id)

    dr.result_created_datetime = datetime.datetime.utcnow()
    db.session.add(dr)
    db.session.commit()

    with patch('identity.demographics.process_demographics_request_data') as mock_process_demographics_request_data, \
        patch('identity.demographics.email') as mock_email, \
        patch('identity.demographics.log_exception') as mock_log_exception, \
        patch('identity.demographics.produce_demographics_result') as mock_produce_demographics_result:

        schedule_lookup_tasks(dr.id)

        mock_process_demographics_request_data.delay.assert_not_called()
        mock_email.assert_not_called()
        mock_log_exception.assert_not_called()
        mock_produce_demographics_result.delay.assert_not_called()
