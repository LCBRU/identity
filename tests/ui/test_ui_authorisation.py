import pytest
from lbrc_flask.pytest.helpers import login
from flask.helpers import url_for


def test_missing_route(client):
    resp = client.get("/uihfihihf")
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "path, filename",
    [
        ('lbrc_flask.static', 'css/main.css'),
        ('lbrc_flask.static', 'img/cropped-favicon-32x32.png'),
        ('lbrc_flask.static', 'img/cropped-favicon-192x192.png'),
        ('lbrc_flask.static', 'img/cropped-favicon-180x180.png'),
        ('lbrc_flask.static', 'img/cropped-favicon-270x270.png'),
        ('lbrc_flask.static', 'favicon.ico'),
    ],
)
def test_url_exists_without_login(client, path, filename):
    resp = client.get(url_for(path, filename=filename))

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


