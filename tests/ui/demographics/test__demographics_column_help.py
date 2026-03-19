import pytest
from functools import cache
from lbrc_flask.pytest.testers import RequiresLoginTester, FlaskViewLoggedInTester, FlaskViewTester, RequiresRoleTester


class DemographicsColumnHelpViewTester(FlaskViewTester):
    @property
    def endpoint(self):
        return 'ui.demographics_column_help'


class TestDemographicsColumnHelpRequiresLogin(DemographicsColumnHelpViewTester, RequiresLoginTester):
    ...


class TestDemographicsColumnHelpRequestGet(DemographicsColumnHelpViewTester, FlaskViewLoggedInTester):
    @pytest.mark.app_crsf(True, )
    def test__get__has_form(self):
        resp = self.get()
