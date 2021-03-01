import pytest
from lbrc_flask.pytest.helpers import login


@pytest.fixture(scope="function")
def loggedin_user(client, faker):
    return login(client, faker)
