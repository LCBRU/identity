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
from .mocks import *


@pytest.fixture(scope="function")
def app():
    return create_app(TestConfig)


@pytest.yield_fixture(scope="function")
def faker():
    result = Faker("en_GB")
    result.add_provider(IdentityProvider)
    result.add_provider(DemographicsCsvProvider)
    result.add_provider(DemographicsXslxProvider)
    result.add_provider(PmiProvider)

    yield result
