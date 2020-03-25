import pytest
from unittest.mock import patch, MagicMock, PropertyMock


@pytest.yield_fixture(scope="function")
def mock_pmi_engine(app):
    with patch('identity.services.pmi.pmi_engine') as mock_engine:
        yield mock_engine
