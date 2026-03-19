import pytest
from functools import cache
from lbrc_flask.pytest.testers import RequiresLoginTester, FlaskViewLoggedInTester, FlaskViewTester, RequiresRoleTester


class DemographicsDownloadRequestViewTester(FlaskViewTester):
    @property
    def endpoint(self):
        return 'ui.demographics_download_request'

    @pytest.fixture(autouse=True)
    def a_set_fixture(self, client, faker):
        self.demographics_request = faker.demographics_request().get(save=True)
        faker.demographics_request().create_file(self.demographics_request, "Hello")
        self.parameters['id'] = self.demographics_request.id


class TestDemographicsDownloadRequestRequiresLogin(DemographicsDownloadRequestViewTester, RequiresLoginTester):
    ...


class TestDemographicsDownloadRequestRequiresAdmin(DemographicsDownloadRequestViewTester, RequiresRoleTester):
    @property
    def user_with_required_role(self):
        return self.demographics_request.owner
    
    @property
    def user_without_required_role(self):
        return self.faker.user().get(save=True)


class TestDemographicsDownloadRequestGet(DemographicsDownloadRequestViewTester, FlaskViewLoggedInTester):
    @cache
    def user_to_login(self, faker):
        return self.demographics_request.owner

    @pytest.mark.app_crsf(True, )
    def test__get__has_form(self):
        resp = self.get()
