from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__requires_login


def _url(external=True, **kwargs):
    return url_for('ui.study', _external=external, **kwargs)


def test__get__requires_login(client, faker):
    s = faker.get_test_study()
    assert__requires_login(client, _url(id=s.id, external=False))


def test__ui_study_menu_visible(client, faker):
    user = login(client, faker)

    study_visible = faker.get_test_study()
    study_invisible = faker.get_test_study()

    user.studies.append(study_visible)

    resp = client.get(url_for('ui.index', _external=True))

    assert resp.status_code == 200

    assert (resp.soup.find("a", href=url_for('ui.study', id=study_visible.id)) is not None)
    assert not (resp.soup.find("a", href=url_for('ui.study', id=study_invisible.id)) is not None)


def test__ui_study_page_visible(client, faker):
    user = login(client, faker)

    study_visible = faker.get_test_study()
    study_invisible = faker.get_test_study()

    user.studies.append(study_visible)

    assert client.get(url_for('ui.study', id=study_visible.id, _external=True)).status_code == 200
    assert client.get(url_for('ui.study', id=study_invisible.id, _external=True)).status_code == 403


def test__ui_print_buttons_visible(client, faker):
    user = login(client, faker)

    study_visible = faker.get_test_study()
    study_invisible = faker.get_test_study()

    pack = faker.get_test_label_pack(study=study_visible)
    pack_invisible = faker.get_test_label_pack(study=study_invisible)

    user.studies.append(study_visible)

    resp = client.get(url_for('ui.study', id=study_visible.id, _external=True))

    assert resp.status_code == 200

    assert (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack.type, count=1, study_id=study_visible.id)) is not None)
    assert (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack.type, count=5, study_id=study_visible.id)) is not None)
    assert (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack.type, count=10, study_id=study_visible.id)) is not None)
    assert (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack.type, count=50, study_id=study_visible.id)) is not None)

    assert not (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack_invisible.type, count=1, study_id=study_invisible.id)) is not None)
    assert not (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack_invisible.type, count=5, study_id=study_invisible.id)) is not None)
    assert not (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack_invisible.type, count=10, study_id=study_invisible.id)) is not None)
    assert not (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack_invisible.type, count=50, study_id=study_invisible.id)) is not None)


def test__ui_blinding_and_unblinding_forms_visible(client, faker):
    user = login(client, faker)

    study_visible = faker.get_test_study()
    study_invisible = faker.get_test_study()

    blind = faker.get_test_blinding_set(study=study_visible)
    blind_invisible = faker.get_test_blinding_set(study=study_invisible)

    user.studies.append(study_visible)

    resp = client.get(url_for('ui.study', id=study_visible.id, _external=True))

    assert resp.status_code == 200

    assert (resp.soup.find("form", action=url_for('ui.blinding', id=study_visible.id)) is not None)
    assert (resp.soup.find("form", action=url_for('ui.unblinding', id=study_visible.id)) is not None)
