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
from identity.printing.indapamide import IndapamidePack
from identity.printing.lenten import LentenPack
from identity.printing.limb import LimbPack
from identity.printing.mermaid import MermaidPack
from identity.printing.predict import PredictPack
from identity.printing.preeclampsia import PreeclampsiaPack
from identity.printing.scad import ScadBloodOnlyPack, ScadFamilyPack, ScadPack, ScadRegistryPack
from identity.printing.spiral import SpiralPack
from identity.model import LabelParticipantIdentifier, ParticipantIdentifierType
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


def assert_id_saved(pack, id, user):
    pit = ParticipantIdentifierType.get_study_participant_id()
    assert LabelParticipantIdentifier.query.filter_by(
        participant_identifier_type_id=pit.id,
        study_id=pack.study_id,
        identifier=id,
        last_updated_by_user_id=user.id,
    ).one_or_none() is not None


@pytest.mark.parametrize(
    "PackClass, id_saved",
    [
        (AlleviatePack, True),
        (BravePack, True),
        (BraveExternalPack, True),
        (BravePolandPack, True),
        (CaePack, True),
        (CardiometPack, True),
        (CiaPack, True),
        (DiscordancePack, True),
        (ElasticAsPack, True),
        (FastPack, True),
        (IndapamidePack, True),
        (LentenPack, True),
        (LimbPack, True),
        (PredictPack, True),
        (PreeclampsiaPack, True),
        (ScadBloodOnlyPack, True),
        (ScadFamilyPack, False),
        (ScadPack, True),
        (ScadRegistryPack, False),
        (SpiralPack, True),
    ],
)
def test__pack__print(client, faker, mock_print_label, mock_datetime, PackClass, id_saved):
    u = login(client, faker)

    t = PackClass.query.first()

    mock_datetime.date.today.return_value = datetime.date(2000, 1, 1)

    t.print(1)

    mock_print_label.assert_called()

    assert_calls_data(f'test__{PackClass.__name__}__print', mock_print_label.mock_calls)

    if id_saved:
        # Only check if a record has been created because we can't know what the
        # participant ID will be in these cases
        pit = ParticipantIdentifierType.get_study_participant_id()
        assert LabelParticipantIdentifier.query.filter_by(
            participant_identifier_type_id=pit.id,
            study_id=t.study_id,
            last_updated_by_user_id=u.id,
        ).one_or_none() is not None


@pytest.mark.parametrize(
    "PackClass",
    [
        (GoDcmPack),
    ],
)
def test__pack__print_with_id(client, faker, mock_print_label, mock_datetime, PackClass):
    u = login(client, faker)

    EXPECTED_ID = 'ABC12345C'

    t = PackClass.query.first()
    t.set_participant_id(EXPECTED_ID)

    mock_datetime.date.today.return_value = datetime.date(2000, 1, 1)

    t.print(1)

    mock_print_label.assert_called()

    assert_calls_data(f'test__{PackClass.__name__}__print', mock_print_label.mock_calls)
    assert_id_saved(t, EXPECTED_ID, u)


@pytest.mark.parametrize(
    "PackClass, id_saved",
    [
        (BriccsPack, True),
        (BriccsKetteringPack, True),
        (BriccsSamplePack, False),
        (MermaidPack, True),
    ],
)
def test__briccs_pack__print(client, faker, mock_print_label, mock_briccs_id_provider, PackClass, id_saved):
    u = login(client, faker)

    EXPECTED_ID = 'BPt1245678'
    mock_briccs_id_provider.allocate_id.return_value.barcode = EXPECTED_ID

    t = PackClass.query.first()

    t.print(1)

    mock_print_label.assert_called()

    assert_calls_data(f'test__{PackClass.__name__}__print', mock_print_label.mock_calls)
    if id_saved:
        assert_id_saved(t, EXPECTED_ID, u)


def test__bioresource_pack__print(client, faker, mock_print_label, mock_bioresource_id_provider):
    u = login(client, faker)

    EXPECTED_ID = 'BR1245678A'
    mock_bioresource_id_provider.allocate_id.return_value.barcode = EXPECTED_ID

    t = BioresourcePack.query.first()

    t.print(1)

    mock_print_label.assert_called()

    assert_calls_data(f'test__{BioresourcePack.__name__}__print', mock_print_label.mock_calls)
