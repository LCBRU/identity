from lbrc_flask.pytest.asserts import get_and_assert_standards
from flask import url_for


def lbrc_identity_get(client, url, user, has_form=False):
    resp = get_and_assert_standards(client, url, user, has_form)

    assert resp.soup.nav is not None
    assert resp.soup.nav.find("a", string="Studies") is not None
    assert resp.soup.nav.find("a", string="Tools") is not None
    assert resp.soup.nav.find("a", href=url_for('ui.labels'), string="Labels") is not None

    return resp
