from flask import url_for
from lbrc_flask.database import db
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__requires_login
from tests import lbrc_identity_get


def _url(external=True, **kwargs):
    return url_for('ui.labels', _external=external, **kwargs)


def test__get__requires_login(client):
    assert__requires_login(client, _url(external=False))


def test__labels__logged_in(client, faker):
    user = login(client, faker)
    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200


def test__one_pack__displays(client, faker):
    user = login(client, faker)

    s = faker.get_test_study(owner=user)
    lb = faker.get_test_label_bundle(study=s)
    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200
    assert resp.soup.find("h3", string=lb.study.name) is not None

    assert__label_print_buttons(lb, resp)

def assert__label_print_buttons(lb, resp):
    for i in [1, 5, 10, 50]:
        assert resp.soup.find("a", href=url_for(
            'ui.label_bundle_print',
            study_id=lb.study_id,
            label_bundle_id=lb.id,
            count=i,
            referrer='labels',
        )) is not None


def test__two_packs__displays(client, faker):
    user = login(client, faker)

    s = faker.get_test_study(owner=user)
    lb = faker.get_test_label_bundle(study=s)
    lb2 = faker.get_test_label_bundle(study=s)
    db.session.add(lb2)

    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200
    assert resp.soup.find("h3", string=lb.study.name) is not None

    assert__label_print_buttons(lb, resp)
    assert__label_print_buttons(lb2, resp)


def test__two_studies__displays(client, faker):
    user = login(client, faker)

    s1 = faker.get_test_study(owner=user)
    s2 = faker.get_test_study(owner=user)
    lb1 = faker.get_test_label_bundle(study=s1)
    lb2 = faker.get_test_label_bundle(study=s2)

    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200
    assert resp.soup.find("h3", string=lb1.study.name) is not None
    assert resp.soup.find("h3", string=lb2.study.name) is not None

    assert__label_print_buttons(lb1, resp)
    assert__label_print_buttons(lb2, resp)


def test__study_no_packs__doesnt_display(client, faker):
    user = login(client, faker)

    s = faker.get_test_study(owner=user)

    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200
    assert resp.soup.find("h3", string=s.name) is None


def test__study_not_owner__doesnt_display(client, faker):
    user = login(client, faker)
    other_user = faker.get_test_user()

    s = faker.get_test_study(owner=other_user)
    lb = faker.get_test_label_bundle(study=s)

    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200
    assert resp.soup.find("h3", string=s.name) is None
