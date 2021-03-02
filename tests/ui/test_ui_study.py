import pytest
from flask import url_for
from lbrc_flask.database import db
from lbrc_flask.pytest.helpers import login
from identity.model import Study
from lbrc_flask.pytest.asserts import assert__requires_login


def _url(external=True, **kwargs):
    return url_for('ui.study', _external=external, **kwargs)


def test__get__requires_login(client):
    s = Study.query.filter_by(name="MERMAID").first()
    assert__requires_login(client, _url(id=s.id, external=False))


@pytest.mark.parametrize(
    "study_name, visible",
    [
        ("SCAD", True),
        ("MERMAID", True),
        ("BRICCS", False),
    ],
)
def test__ui_study_menu_visible(client, faker, study_name, visible):
    user = login(client, faker)

    user.studies.add(Study.query.filter_by(name="MERMAID").first())
    user.studies.add(Study.query.filter_by(name="SCAD").first())
    db.session.commit()

    resp = client.get(url_for('ui.index', _external=True))

    assert resp.status_code == 200

    study = Study.query.filter_by(name=study_name).first()

    assert (resp.soup.find("a", href=url_for('ui.study', id=study.id)) is not None) == visible


@pytest.mark.parametrize(
    "study_name, visible",
    [
        ("SCAD", True),
        ("MERMAID", True),
        ("BRICCS", False),
    ],
)
def test__ui_study_page_visible(client, faker, study_name, visible):
    user = login(client, faker)

    user.studies.add(Study.query.filter_by(name="MERMAID").first())
    user.studies.add(Study.query.filter_by(name="SCAD").first())
    db.session.commit()

    study = Study.query.filter_by(name=study_name).first()

    resp = client.get(url_for('ui.study', id=study.id, _external=True))

    if visible:
        assert resp.status_code == 200
    else:
        assert resp.status_code == 403


@pytest.mark.parametrize(
    "pack_name, visible",
    [
        ("ScadPack", True),
        ("ScadBloodOnlyPack", True),
        ("ScadFamilyPack", True),
        ("MermaidPack", False),
        ("BriccsPack", False),
    ],
)
def test__ui_print_buttons_visible(client, faker, pack_name, visible):
    user = login(client, faker)

    scad_study = Study.query.filter_by(name="SCAD").first()

    user.studies.add(Study.query.filter_by(name="MERMAID").first())
    user.studies.add(scad_study)
    db.session.commit()

    resp = client.get(url_for('ui.study', id=scad_study.id, _external=True))

    assert resp.status_code == 200

    assert (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack_name, count=1, study_id=scad_study.id)) is not None) == visible
    assert (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack_name, count=5, study_id=scad_study.id)) is not None) == visible
    assert (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack_name, count=10, study_id=scad_study.id)) is not None) == visible
    assert (resp.soup.find("a", href=url_for('ui.label_print', referrer='study', pack_name=pack_name, count=50, study_id=scad_study.id)) is not None) == visible


@pytest.mark.parametrize(
    "study_name, visible",
    [
        ("SCAD", True),
        ("MERMAID", False),
    ],
)
def test__ui_blinding_and_unblinding_forms_visible(client, faker, study_name, visible):
    user = login(client, faker)

    study = Study.query.filter_by(name=study_name).first()

    user.studies.add(Study.query.filter_by(name="DISCORDANCE").first())
    user.studies.add(study)
    db.session.commit()

    resp = client.get(url_for('ui.study', id=study.id, _external=True))

    assert resp.status_code == 200

    assert (resp.soup.find("form", action=url_for('ui.blinding', id=study.id)) is not None) == visible
    assert (resp.soup.find("form", action=url_for('ui.unblinding', id=study.id)) is not None) == visible
