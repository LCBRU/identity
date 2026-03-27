import pytest
from datetime import datetime, UTC
from lbrc_flask.database import db
from identity.demographics import do_lookup_tasks
from lbrc_flask.pytest.helpers import login
from tests.demographics import (
    DemographicsTestHelper,
)


class TestScheduling:

    @pytest.fixture(autouse=True)
    def fixtures(self, client, faker, mock_process_demographics_request_data, mock_extract_data, mock_produce_demographics_result, mock_extract_pre_pmi_details, mock_extract_post_pmi_details, mock_log_exception):
        self.client = client
        self.faker = faker

        self.user = login(self.client, self.faker)
        self.test_helper = DemographicsTestHelper(faker=self.faker, user=self.user)

        self.all_mocks = {}
        self.all_mocks['mock_process_demographics_request_data'] = mock_process_demographics_request_data
        self.all_mocks['mock_extract_data'] = mock_extract_data
        self.all_mocks['mock_produce_demographics_result'] = mock_produce_demographics_result
        self.all_mocks['mock_extract_pre_pmi_details'] = mock_extract_pre_pmi_details
        self.all_mocks['mock_extract_post_pmi_details'] = mock_extract_post_pmi_details
        self.mock_log_exception = mock_log_exception

    def assert_not_called(self, called=None):
        called = called or []

        not_called_mocks = [v for k, v in self.all_mocks.items() if k not in called]
        called_mocks = [v for k, v in self.all_mocks.items() if k in called]

        print(called_mocks)

        for m in not_called_mocks:
            m.delay.assert_not_called()

        for m in called_mocks:
            m.delay.assert_called_once()

        if 'mock_log_exception' in called:
            self.mock_log_exception.assert_called_once()
        else:
            self.mock_log_exception.assert_not_called()

    def test__schedule_lookup_tasks__request_not_found(self):
        do_lookup_tasks(1)
        self.assert_not_called(['mock_log_exception'])

    def test__schedule_lookup_tasks__in_error(self):
        dr = self.test_helper.get_demographics_request__uploaded()
        dr.error_datetime = datetime.now(UTC)
        db.session.add(dr)
        db.session.commit()

        do_lookup_tasks(dr.id)

        self.assert_not_called()

    def test__schedule_lookup_tasks__paused(self):
        dr = self.test_helper.get_demographics_request__uploaded()
        dr.paused_datetime = datetime.now(UTC)
        db.session.add(dr)
        db.session.commit()

        do_lookup_tasks(dr.id)

        self.assert_not_called()

    def test__schedule_lookup_tasks__deleted(self):
        dr = self.test_helper.get_demographics_request__uploaded()
        dr.deleted_datetime = datetime.now(UTC)
        db.session.add(dr)
        db.session.commit()

        do_lookup_tasks(dr.id)

        self.assert_not_called()

    def test__schedule_lookup_tasks__submitted(self):
        dr = self.test_helper.get_demographics_request__data_extraction()

        do_lookup_tasks(dr.id)

        self.assert_not_called(['mock_extract_data'])

    def test__schedule_lookup_tasks__extracted(self):
        dr = self.test_helper.get_demographics_request__pre_pmi_lookup()

        do_lookup_tasks(dr.id)

        self.assert_not_called(['mock_extract_pre_pmi_details'])
        self.all_mocks['mock_extract_pre_pmi_details'].delay.assert_called_once_with(dr.id)

    def test__schedule_lookup_tasks__extracted__skip_pmi(self):
        self.test_helper._skip_pmi = True
        dr = self.test_helper.get_demographics_request__pre_pmi_lookup()

        do_lookup_tasks(dr.id)

        self.assert_not_called(['mock_process_demographics_request_data'])
        self.all_mocks['mock_process_demographics_request_data'].delay.assert_called_once_with(dr.id)

    def test__schedule_lookup_tasks__got_pre_pmi(self):
        dr = self.test_helper.get_demographics_request__spine_lookup()

        do_lookup_tasks(dr.id)

        self.assert_not_called(['mock_process_demographics_request_data'])
        self.all_mocks['mock_process_demographics_request_data'].delay.assert_called_once_with(dr.id)

    def test__schedule_lookup_tasks__spine_looked_up(self):
        dr = self.test_helper.get_demographics_request__post_pmi_lookup()

        do_lookup_tasks(dr.id)

        self.assert_not_called(['mock_extract_post_pmi_details'])
        self.all_mocks['mock_extract_post_pmi_details'].delay.assert_called_once_with(dr.id)

    def test__schedule_lookup_tasks__spine_looked_up__skip_pmi(self):
        self.test_helper._skip_pmi = True
        dr = self.test_helper.get_demographics_request__post_pmi_lookup()

        do_lookup_tasks(dr.id)

        self.assert_not_called(['mock_produce_demographics_result'])
        self.all_mocks['mock_produce_demographics_result'].delay.assert_called_once_with(dr.id)

    def test__schedule_lookup_tasks__got_post_pmi(self):
        dr = self.test_helper.get_demographics_request__create_results()

        do_lookup_tasks(dr.id)

        self.assert_not_called(['mock_produce_demographics_result'])
        self.all_mocks['mock_produce_demographics_result'].delay.assert_called_once_with(dr.id)

    def test__schedule_lookup_tasks__result_created(self):
        dr = self.test_helper.get_demographics_request__download()

        do_lookup_tasks(dr.id)

        self.assert_not_called()
