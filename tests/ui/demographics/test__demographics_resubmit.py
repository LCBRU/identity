from functools import cache
from unittest.mock import Mock, patch

import pytest
import http
from lbrc_flask.pytest.testers import RequiresLoginTester, FlaskViewLoggedInTester, FlaskViewTester, RequiresRoleTester


class DemographicsResubmitViewTester(FlaskViewTester):
    @property
    def endpoint(self):
        return 'ui.demographics_resubmit'

    @pytest.fixture(autouse=True)
    def set_existing(self, client, faker):
        self.demographics_request = faker.demographics_request().get(save=True)
        self.parameters['id'] = self.demographics_request.id


class TestDemographicsResubmitRequiresLogin(DemographicsResubmitViewTester, RequiresLoginTester):
    ...


class TestDemographicsResubmitRequiresAdmin(DemographicsResubmitViewTester, RequiresRoleTester):
    @property
    def user_with_required_role(self):
        return self.faker.user().admin(save=True)
    
    @property
    def user_without_required_role(self):
        return self.faker.user().get(save=True)

    @patch('identity.ui.views.demographics.schedule_lookup_tasks') # Mocking as cereal tasks do not work in testing
    def test__get__logged_in_user_with_required_role__allowed(self, schedule_lookup_tasks):
        self.login(self.user_with_required_role)
        self.request_method(expected_status_code=http.HTTPStatus.FOUND)


@patch('identity.ui.views.demographics.schedule_lookup_tasks') # Mocking as cereal tasks do not work in testing
class TestDemographicsResubmitGet(DemographicsResubmitViewTester, FlaskViewLoggedInTester):
    @cache
    def user_to_login(self, faker):
        return faker.user().admin(save=True)

    @pytest.mark.app_crsf(True, )
    def test__get__has_form(self, schedule_lookup_tasks: Mock):
        resp = self.get(expected_status_code=http.HTTPStatus.FOUND)

        schedule_lookup_tasks.assert_called_once()
