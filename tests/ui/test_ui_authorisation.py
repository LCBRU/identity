import pytest
from lbrc_flask.pytest.helpers import login


def test_missing_route(client):
    resp = client.get("/uihfihihf")
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        ("/static/css/main.css"),
        ("/static/img/bars-top.svg"),
        ("/static/img/nihr-lbrc-cropped.png"),
        ("/static/img/cropped-favicon-32x32.png"),
        ("/static/img/cropped-favicon-192x192.png"),
        ("/static/img/cropped-favicon-180x180.png"),
        ("/static/img/cropped-favicon-270x270.png"),
        ("/static/favicon.ico"),
    ],
)
def test_url_exists_without_login(client, path):
    resp = client.get(path)

    assert resp.status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        ("/"),
        ("/labels/"),
        ("/demographics/"),
        ("/labels/study/1/MermaidPack/print/1/referrer/refrrerer"),
    ],
)
def test_url_requires_login_get(client, path):
    resp = client.get(path)
    assert resp.status_code == 302


@pytest.mark.parametrize(
    "path",
    [
        ("/"),
        ("/labels/"),
        ("/demographics/"),
    ]
)
def test_url_requires_login_logged_in(client, faker, path):
    login(client, faker)
    resp = client.get(path)
    assert resp.status_code == 200


