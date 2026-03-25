import pytest
from faker import Faker
from lbrc_flask.pytest.fixtures import client, initialised_app
from identity.config import TestConfig
from identity import create_app
from tests.faker_civicrm import CivicrmProvider
from tests.faker_demographics import DemographicsProvider
from tests.faker_etl_central import EtlCentralProvider
from .faker import IdentityProvider
from lbrc_flask.pytest.faker import LbrcFlaskFakerProvider
from .mocks import *
from lbrc_flask.pytest.fakers.column_data_faker import LbrcFileProvider


@pytest.fixture(scope="function")
def app(tmp_path):
    class LocalTestConfig(TestConfig):
        FILE_UPLOAD_DIRECTORY = tmp_path

    yield create_app(LocalTestConfig)


@pytest.fixture(scope="function")
def faker():
    result = Faker("en_GB")
    result.add_provider(LbrcFlaskFakerProvider)
    result.add_provider(LbrcFileProvider)
    result.add_provider(IdentityProvider)
    result.add_provider(CivicrmProvider)
    result.add_provider(EtlCentralProvider)
    result.add_provider(DemographicsProvider)
    

    yield result
