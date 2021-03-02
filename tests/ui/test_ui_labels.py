from identity.printing.alleviate import AlleviatePack
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
    lp = faker.get_test_label_pack(study=s)
    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200
    assert resp.soup.find("h3", string=lp.study.name) is not None

    assert__label_print_buttons(lp, resp)

def assert__label_print_buttons(lp, resp):
    for i in [1, 5, 10, 50]:
        assert resp.soup.find("a", href=url_for(
            'ui.label_print',
            study_id=lp.study_id,
            pack_name=lp.type,
            count=i,
            referrer='labels',
        )) is not None


def test__two_packs__displays(client, faker):
    user = login(client, faker)

    s = faker.get_test_study(owner=user)
    lp = faker.get_test_label_pack(study=s)
    ap = AlleviatePack(study_id=s.id)
    db.session.add(ap)

    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200
    assert resp.soup.find("h3", string=lp.study.name) is not None

    assert__label_print_buttons(lp, resp)
    assert__label_print_buttons(ap, resp)


def test__two_studies__displays(client, faker):
    user = login(client, faker)

    s1 = faker.get_test_study(owner=user)
    s2 = faker.get_test_study(owner=user)
    lp1 = faker.get_test_label_pack(study=s1)
    lp2 = faker.get_test_label_pack(study=s2)

    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200
    assert resp.soup.find("h3", string=lp1.study.name) is not None
    assert resp.soup.find("h3", string=lp2.study.name) is not None

    assert__label_print_buttons(lp1, resp)
    assert__label_print_buttons(lp2, resp)


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
    lp = faker.get_test_label_pack(study=s)

    resp = lbrc_identity_get(client, _url(), user)

    assert resp.status_code == 200
    assert resp.soup.find("h3", string=s.name) is None
