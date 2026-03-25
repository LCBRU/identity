import http
import pytest
from lbrc_flask.pytest.testers import FlaskViewTester


class TestParticipantEditGet(FlaskViewTester):
    @property
    def endpoint(self):
        return 'ui.participant_edit'
    
    @pytest.fixture(autouse=True)
    def set_existing(self, client, faker):
        self.owner = faker.user().get(save=True)
        self.study = faker.study().get(save=True, owner=self.owner)
        self.participant = faker.civicrm_participant().get(save=True, study=self.study)
        self.parameters['id'] = self.study.id
        self.parameters['participant_id'] = self.participant.id

    def test__requires_login(self):
        response = self.get(expected_status_code=http.HTTPStatus.FOUND)
        self.assert_requires_login_response(response)

    def test__get__logged_in_user_without_required_role__permission_denied(self):
        self.login(self.faker.user().get(save=True))
        self.get(expected_status_code=http.HTTPStatus.FORBIDDEN)

    def test__get__logged_in_user_with_required_role__allowed(self):
        self.login(self.owner)
        self.get()

    @pytest.mark.app_crsf(True, )
    def test__get__has_form(self):
        self.login(self.owner)

        resp = self.get()
