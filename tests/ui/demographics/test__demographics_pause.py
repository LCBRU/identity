import pytest
import http
from functools import cache
from unittest.mock import Mock, patch
from lbrc_flask.pytest.testers import RequiresLoginTester, FlaskViewLoggedInTester, FlaskViewTester, RequiresRoleTester


class DemographicsPauseViewTester(FlaskViewTester):
    @property
    def endpoint(self):
        return 'ui.demographics_pause'

    @pytest.fixture(autouse=True)
    def set_existing(self, client, faker):
        self.demographics_request = faker.demographics_request().get(save=True)
        self.parameters['id'] = self.demographics_request.id


class TestDemographicsPauseRequiresLogin(DemographicsPauseViewTester, RequiresLoginTester):
    ...


class TestDemographicsPauseRequiresAdmin(DemographicsPauseViewTester, RequiresRoleTester):
    @property
    def user_with_required_role(self):
        return self.faker.user().admin(save=True)
    
    @property
    def user_without_required_role(self):
        return self.faker.user().get(save=True)

    def test__get__logged_in_user_with_required_role__allowed(self):
        self.login(self.user_with_required_role)
        self.request_method(expected_status_code=http.HTTPStatus.FOUND)


class TestDemographicsPauseGet(DemographicsPauseViewTester, FlaskViewLoggedInTester):
    @cache
    def user_to_login(self, faker):
        return faker.user().admin(save=True)

    @pytest.mark.app_crsf(True, )
    def test__get__has_form(self):
        resp = self.get(expected_status_code=http.HTTPStatus.FOUND)
