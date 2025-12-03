import contextlib
import os
from lbrc_flask.database import db
from identity.demographics import process_demographics_request_data
from identity.demographics.model import (
    DemographicsRequest,
    DemographicsRequestDataMessage,
)
from lbrc_flask.pytest.helpers import login
from tests.demographics import (
    DemographicsTestHelper,
)


def test__process_demographics_request_data__request_not_found(client, faker, mock_schedule_lookup_tasks, mock_spine_lookup, mock_log_exception):

    process_demographics_request_data(1)

    mock_spine_lookup.assert_not_called()
    mock_schedule_lookup_tasks.assert_not_called()
    mock_log_exception.assert_called_once()


def test__process_demographics_request_data__spine_exception(client, faker, mock_schedule_lookup_tasks, mock_spine_lookup, mock_log_exception):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__spine_lookup()

    e = Exception()

    mock_spine_lookup.side_effect = e
    process_demographics_request_data(dr.id)

    mock_spine_lookup.assert_called_once_with(dr.data[0])
    mock_schedule_lookup_tasks.assert_not_called()
    mock_log_exception.assert_called_once_with(e)

    _remove_files(dr)


def test__process_demographics_request_data__no_data(client, faker, mock_schedule_lookup_tasks, mock_spine_lookup, mock_log_exception):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=0)
    dr = dth.get_demographics_request__spine_lookup()

    process_demographics_request_data(dr.id)

    mock_spine_lookup.assert_not_called()
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)
    mock_log_exception.assert_not_called()

    actual: DemographicsRequest = db.session.get(DemographicsRequest, dr.id)

    assert actual.lookup_completed_datetime is not None

    _remove_files(dr)


def test__process_demographics_request_data__with_data(client, faker, mock_schedule_lookup_tasks, mock_spine_lookup, mock_log_exception):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=2)
    dr = dth.get_demographics_request__spine_lookup()

    process_demographics_request_data(dr.id)

    mock_spine_lookup.assert_called_once_with(dr.data[0])
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)
    mock_log_exception.assert_not_called()

    actual: DemographicsRequest = db.session.get(DemographicsRequest, dr.id)

    assert actual.lookup_completed_datetime is None
    assert actual.data[0].processed_datetime is not None
    assert actual.data[1].processed_datetime is None

    _remove_files(dr)


def test__process_demographics_request_data__data_has_error(client, faker, mock_schedule_lookup_tasks, mock_spine_lookup, mock_log_exception):
    u = login(client, faker)
    dth = DemographicsTestHelper(faker=faker, user=u, row_count=1)
    dr = dth.get_demographics_request__spine_lookup()

    db.session.add(DemographicsRequestDataMessage(
        demographics_request_data=dr.data[0],
        type='error',
        source='TEST',
        scope='DATA',
        message='A message',
    ))
    db.session.commit()

    process_demographics_request_data(dr.id)

    mock_spine_lookup.assert_called_once_with(dr.data[0])
    mock_schedule_lookup_tasks.assert_called_once_with(dr.id)
    mock_log_exception.assert_not_called()

    actual: DemographicsRequest = db.session.get(DemographicsRequest, dr.id)

    assert actual.lookup_completed_datetime is None
    assert actual.data[0].processed_datetime is not None

    _remove_files(dr)


def _remove_files(dr):
    with contextlib.suppress(FileNotFoundError):
        os.remove(dr.filepath)
        os.remove(dr.result_filepath)
