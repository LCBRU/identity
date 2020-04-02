import os
import pytest
import pathlib
import datetime
import pickle5 as pickle
from unittest.mock import patch, MagicMock
from identity.printing.alleviate import AlleviatePack
from identity.printing.bioresource import BioresourcePack
from identity.printing.brave import BravePack, BraveExternalPack, BravePolandPack
from identity.printing.briccs import BriccsPack, BriccsKetteringPack, BriccsSamplePack
from identity.printing.cae import CaePack
from identity.printing.cardiomet import CardiometPack
from identity.printing.cia import CiaPack
from identity.printing.discordance import DiscordancePack
from identity.printing.elastic_as import ElasticAsPack
from identity.printing.fast import FastPack
from identity.printing.go_dcm import GoDcmPack
from tests import login


@pytest.yield_fixture(scope="function")
def mock_print_label(app):
    with patch('identity.printing.printing_methods.print_label') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_datetime(app):
    with patch('identity.printing.printing_methods.datetime') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_bioresource_id_provider(app):
    with patch('identity.printing.bioresource.BioresourceIdProvider') as mock:
        mid = MagicMock(name='Mock ID Provider')
        mock.query.filter_by.return_value.first.return_value = mid
        yield mid


@pytest.yield_fixture(scope="function")
def mock_briccs_id_provider(app):
    with patch('identity.printing.briccs.LegacyIdProvider') as mock:
        mid = MagicMock(name='BRICCS ID Provider')
        mock.query.filter_by.return_value.first.return_value = mid
        yield mid


def assert_calls_data(test_name, calls):
    actual = sorted([str(c) for c in calls])

    filename = os.path.join(pathlib.Path(__file__).parent.absolute(), f'{test_name}_testdata.pickle')

    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            pickle.dump(actual, f, pickle.HIGHEST_PROTOCOL)

        return

    with open(filename, 'rb') as f:
        expected = pickle.load(f)
    
    assert expected == actual


@pytest.mark.parametrize(
    "PackClass",
    [
        (AlleviatePack),
        (BravePack),
        (BraveExternalPack),
        (BravePolandPack),
        (CaePack),
        (CardiometPack),
        (CiaPack),
        (DiscordancePack),
        (ElasticAsPack),
        (FastPack),
    ],
)
def test__pack__print(client, faker, mock_print_label, mock_datetime, PackClass):
    login(client, faker)

    t = PackClass.query.first()

    mock_datetime.date.today.return_value = datetime.date(2000, 1, 1)

    t.print(1)

    mock_print_label.assert_called()

    assert_calls_data(f'test__{PackClass.__name__}__print', mock_print_label.mock_calls)


@pytest.mark.parametrize(
    "PackClass",
    [
        (GoDcmPack),
    ],
)
def test__pack__print_with_id(client, faker, mock_print_label, mock_datetime, PackClass):
    login(client, faker)

    t = PackClass.query.first()
    t.set_participant_id('ABC12345C')

    mock_datetime.date.today.return_value = datetime.date(2000, 1, 1)

    t.print(1)

    mock_print_label.assert_called()

    assert_calls_data(f'test__{PackClass.__name__}__print', mock_print_label.mock_calls)


@pytest.mark.parametrize(
    "PackClass",
    [
        (BriccsPack),
        (BriccsKetteringPack),
        (BriccsSamplePack),
    ],
)
def test__briccs_pack__print(client, faker, mock_print_label, mock_briccs_id_provider, PackClass):
    login(client, faker)

    mock_briccs_id_provider.allocate_id.return_value.barcode = 'BPt1245678'

    t = PackClass.query.first()

    t.print(1)

    mock_print_label.assert_called()

    assert_calls_data(f'test__{PackClass.__name__}__print', mock_print_label.mock_calls)


def test__bioresource_pack__print(client, faker, mock_print_label, mock_bioresource_id_provider):
    login(client, faker)

    mock_bioresource_id_provider.allocate_id.return_value.barcode = 'BR1245678A'

    t = BioresourcePack.query.first()

    t.print(1)

    mock_print_label.assert_called()

    assert_calls_data(f'test__{BioresourcePack.__name__}__print', mock_print_label.mock_calls)
