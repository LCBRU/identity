import contextlib
from datetime import datetime
import os
from identity.database import db
from identity.demographics import schedule_lookup_tasks
from tests import login
from tests.demographics import (
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
    DemographicsTestHelper,
)

def test__schedule_lookup_tasks__request_not_found(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    schedule_lookup_tasks(1)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_called_once()


def test__schedule_lookup_tasks__in_error(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__uploaded()
    dr.error_datetime = datetime.utcnow()
    db.session.add(dr)
    db.session.commit()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__paused(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__uploaded()
    dr.paused_datetime = datetime.utcnow()
    db.session.add(dr)
    db.session.commit()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__deleted(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__uploaded()
    dr.deleted_datetime = datetime.utcnow()
    db.session.add(dr)
    db.session.commit()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__submitted(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__data_extraction()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_called_once_with(dr.id)
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__extracted(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_called_once_with(dr.id)
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__extracted__skip_pmi(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, skip_pmi=True)
    dr = dth.get_demographics_request__pre_pmi_lookup()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_called_once_with(dr.id)
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__got_pre_pmi(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__spine_lookup()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_called_once_with(dr.id)
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__spine_looked_up(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__post_pmi_lookup()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_called_once_with(dr.id)
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__spine_looked_up__skip_pmi(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, skip_pmi=True)
    dr = dth.get_demographics_request__post_pmi_lookup()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_called_once_with(dr.id)
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__got_post_pmi(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__create_results()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_called_once_with(dr.id)
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def test__schedule_lookup_tasks__result_created(
    client,
    faker,
    mock_process_demographics_request_data,
    mock_extract_data,
    mock_produce_demographics_result,
    mock_extract_pre_pmi_details,
    mock_extract_post_pmi_details,
    mock_log_exception,
):

    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u)
    dr = dth.get_demographics_request__download()

    schedule_lookup_tasks(dr.id)

    mock_extract_data.delay.assert_not_called()
    mock_extract_pre_pmi_details.delay.assert_not_called()
    mock_process_demographics_request_data.delay.assert_not_called()
    mock_extract_post_pmi_details.delay.assert_not_called()
    mock_produce_demographics_result.delay.assert_not_called()
    mock_log_exception.assert_not_called()

    _remove_files(dr)


def _remove_files(dr):
    with contextlib.suppress(FileNotFoundError):
        os.remove(dr.filepath)
        os.remove(dr.result_filepath)
