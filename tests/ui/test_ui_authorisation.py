import pytest
from lbrc_flask.pytest.helpers import login


@pytest.mark.parametrize(
    "path",
    [
        ("/"),
        ("/demographics/"),
    ],
)
def test_url_requires_login_get(client, path):
    resp = client.get(path)
    assert resp.status_code == 302


@pytest.mark.parametrize(
    "path",
    [
        ("/"),
        ("/demographics/"),
    ]
)
def test_url_requires_login_logged_in(client, faker, path):
    login(client, faker)
    resp = client.get(path)
    assert resp.status_code == 200
