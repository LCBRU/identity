# -*- coding: utf-8 -*-

import pytest
import urllib.parse
from flask import url_for
from identity.database import db
from tests import login
from identity.model import Study


@pytest.mark.parametrize(
    "pack_name, visible",
    [
        ("ScadPack", True),
        ("ScadBloodOnlyPack", True),
        ("ScadFamilyPack", True),
        ("MermaidPack", True),
        ("BriccsPack", False),
    ],
)
def test__ui_buttons_visible(client, faker, pack_name, visible):
    user = login(client, faker)

    user.studies.add(Study.query.filter_by(name="MERMAID").first())
    user.studies.add(Study.query.filter_by(name="SCAD").first())
    db.session.commit()

    resp = client.get(url_for('ui.labels', _external=True))

    assert resp.status_code == 200

    assert (resp.soup.find("a", href=url_for('ui.label_print', set=pack_name, count=1)) is not None) == visible


@pytest.mark.parametrize(
    "pack_name, printable",
    [
        ("ScadPack", True),
        ("ScadBloodOnlyPack", True),
        ("ScadFamilyPack", True),
        ("MermaidPack", True),
        ("BriccsPack", False),
    ],
)
def test__ui_page_accessible(client, faker, pack_name, printable):
    user = login(client, faker)

    user.studies.add(Study.query.filter_by(name="MERMAID").first())
    user.studies.add(Study.query.filter_by(name="SCAD").first())
    db.session.commit()

    resp = client.get(url_for('ui.label_print', set=pack_name, count=1, _external=True))

    if printable:
        assert resp.status_code == 302
        assert resp.location == url_for('ui.labels', _external=True)
    else:
        assert resp.status_code == 403
