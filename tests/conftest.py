import pytest
from faker import Faker
from lbrc_flask.pytest.fixtures import *
from identity.config import TestConfig
from identity import create_app
from tests.faker_civicrm import CivicrmProvider
from tests.faker_etl_central import EtlCentralProvider
from .faker import IdentityProvider
from lbrc_flask.pytest.faker import LbrcFlaskFakerProvider
from .mocks import *
from lbrc_flask.pytest.helpers import login


@pytest.fixture(scope="function")
def app():
    return create_app(TestConfig)


@pytest.fixture(scope="function")
def loggedin_user(client, faker):
    return login(client, faker)


@pytest.fixture(scope="function")
def faker():
    result = Faker("en_GB")
    result.add_provider(LbrcFlaskFakerProvider)
    result.add_provider(IdentityProvider)
    result.add_provider(CivicrmProvider)
    result.add_provider(EtlCentralProvider)

    yield result
