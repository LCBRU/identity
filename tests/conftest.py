import pytest
from faker import Faker
from lbrc_flask.pytest.fixtures import *
from identity.config import TestConfig
from identity import create_app
from .faker import (
    IdentityProvider,
    DemographicsCsvProvider,
    DemographicsXslxProvider,
    PmiProvider,
)
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
    result.add_provider(DemographicsCsvProvider)
    result.add_provider(DemographicsXslxProvider)
    result.add_provider(PmiProvider)

    yield result
