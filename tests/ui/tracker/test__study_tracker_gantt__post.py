import http
import pytest
from lbrc_flask.pytest.testers import FlaskViewTester


class TestStudyTrackerGanttPost(FlaskViewTester):
    @property
    def endpoint(self):
        return 'ui.study_tracker_gantt'
    
    def test__requires_login(self):
        response = self.post(expected_status_code=http.HTTPStatus.FOUND)
        self.assert_requires_login_response(response)

    @pytest.mark.app_crsf(True, )
    def test__get__has_form(self):
        self.login(self.faker.user().get(save=True))

        resp = self.post()
