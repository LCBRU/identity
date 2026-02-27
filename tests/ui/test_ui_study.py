from flask import url_for
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__requires_login


def _url(external=True, **kwargs):
    return url_for('ui.study', _external=external, **kwargs)


def test__get__requires_login(client, faker):
    s = faker.study().get(save=True)
    assert__requires_login(client, _url(id=s.id, external=False))


def test__ui_study_menu_visible(client, faker):
    user = login(client, faker)

    study_visible = faker.study().get(save=True)
    study_invisible = faker.study().get(save=True)

    user.studies.append(study_visible)

    resp = client.get(url_for('ui.index', _external=True))

    assert resp.status_code == 200

    assert (resp.soup.find("a", href=url_for('ui.study', id=study_visible.id)) is not None)
    assert not (resp.soup.find("a", href=url_for('ui.study', id=study_invisible.id)) is not None)


def test__ui_study_page_visible(client, faker):
    user = login(client, faker)

    study_visible = faker.study().get(save=True)
    study_invisible = faker.study().get(save=True)

    user.studies.append(study_visible)

    assert client.get(url_for('ui.study', id=study_visible.id, _external=True)).status_code == 200
    assert client.get(url_for('ui.study', id=study_invisible.id, _external=True)).status_code == 403


def test__ui_print_buttons_visible(client, faker):
    user = login(client, faker)

    study_visible = faker.study().get(save=True)
    study_invisible = faker.study().get(save=True)

    bundle = faker.label_bundle().get(save=True, study=study_visible)
    bundle_invisible = faker.label_bundle().get(save=True, study=study_invisible)

    user.studies.append(study_visible)

    resp = client.get(url_for('ui.study', id=study_visible.id, _external=True))

    assert resp.status_code == 200

    assert resp.soup.find('a', attrs={"hx-get" : url_for('ui.label_bundle_definition', id=bundle.id, count=5)}) is not None
    assert resp.soup.find('a', attrs={"hx-get" : url_for('ui.label_bundle_definition', id=bundle_invisible.id, count=5)}) is None


def test__ui_blinding_and_unblinding_forms_visible(client, faker):
    user = login(client, faker)

    study_visible = faker.study().get(save=True)
    study_invisible = faker.study().get(save=True)

    blind = faker.blinding_type().get(save=True, study=study_visible)
    blind_invisible = faker.blinding_type().get(save=True, study=study_invisible)

    user.studies.append(study_visible)

    resp = client.get(url_for('ui.study', id=study_visible.id, _external=True))

    assert resp.status_code == 200

    assert (resp.soup.find("form", action=url_for('ui.blinding', id=study_visible.id)) is not None)
    assert (resp.soup.find("form", action=url_for('ui.unblinding', id=study_visible.id)) is not None)
