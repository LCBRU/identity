import pytest
from lbrc_flask.pytest.helpers import login
from flask.helpers import url_for


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


