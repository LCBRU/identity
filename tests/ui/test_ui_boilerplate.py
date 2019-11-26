# -*- coding: utf-8 -*-

import pytest
from flask import url_for
from identity.database import db
from tests import login


@pytest.mark.parametrize(
    "path",
    [
        ("/"),
        ("/labels/"),
        ("/demographics/"),
    ],
)
def test__boilerplate__html_standards(client, faker, path):
    user = login(client, faker)

    resp = client.get(path)

    assert resp.soup.html is not None
    assert resp.soup.html["lang"] == "en"
    assert resp.soup.head is not None
    assert (
        resp.soup.find(
            lambda tag: tag.name == "meta"
            and tag.has_attr("charset")
            and tag["charset"] == "utf-8"
        )
        is not None
    )
    assert resp.soup.title is not None
    assert resp.soup.body is not None


@pytest.mark.parametrize("path", [("/login")])
def test__boilerplate__login_csrf_token(client_with_crsf, faker, path):
    client = client_with_crsf

    resp = client.get(path)

    assert (
        resp.soup.find("input", {"name": "csrf_token"}, type="hidden", id="csrf_token")
        is not None
    )


@pytest.mark.parametrize(
    "path",
    [
        ("/"),
        ("/labels/"),
        ("/demographics/"),
    ],
)
def test__boilerplate__basic_navigation(client, faker, path):
    user = login(client, faker)

    resp = client.get(path)

    assert resp.soup.nav is not None
    assert resp.soup.nav.find("a", href=url_for('ui.index')) is not None
    assert resp.soup.nav.find("a", href=url_for('ui.labels')) is not None
    assert resp.soup.find(lambda tag:tag.name=="a" and user.full_name in tag.text) is not None
    assert resp.soup.nav.find("a", href=url_for('security_ui.logout')) is not None
