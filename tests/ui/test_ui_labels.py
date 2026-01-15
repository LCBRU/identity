import http
import pytest
from lbrc_flask.pytest.asserts import assert__redirect
from lbrc_flask.pytest.testers import RequiresLoginTester, FlaskViewLoggedInTester


class LabelsViewTester:
    @property
    def endpoint(self):
        return 'ui.labels'
    

class TestLabelsViewRequiresLogin(LabelsViewTester, RequiresLoginTester):
    ...


class TestStudyList(LabelsViewTester, FlaskViewLoggedInTester):
    def test__owns_1_study__redirects_to_study(self):
        study = self.faker.get_test_study(owner=self.loggedin_user)
        resp = self.get(expected_status_code=http.HTTPStatus.FOUND)
        assert__redirect(resp, endpoint='ui.study', id=study.id)

    @pytest.mark.parametrize(
        "study_count",
        [0, 2, 3],
    )
    def test__owns_multiple_studies__no_redirect(self, study_count):
        for _ in range(study_count):
            _ = self.faker.get_test_study(owner=self.loggedin_user)

        resp = self.get(expected_status_code=http.HTTPStatus.FOUND)
        assert__redirect(resp, endpoint='ui.index')
