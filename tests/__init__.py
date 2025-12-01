import warnings
from dotenv import load_dotenv

# Filter out deprecation warnings from dependencies that we have no control over
warnings.filterwarnings("ignore", module="pyasn1.codec.ber.encoder", lineno=952)

# Load environment variables from '.env' file.
load_dotenv()

from lbrc_flask.pytest.asserts import get_and_assert_standards


def lbrc_identity_get(client, url, user, has_form=False):
    resp = get_and_assert_standards(client, url, user, has_form)

    assert resp.soup.nav is not None
    assert resp.soup.nav.find("a", string="Studies") is not None
    assert resp.soup.nav.find("a", string="Tools") is not None
    # assert resp.soup.nav.find("a", href=url_for('ui.labels'), string="Labels") is not None

    return resp
