import pytest
from identity.model import Study
from identity.printing.model import LabelPack
from identity.setup import create_base_data


@pytest.mark.parametrize(
    "study, pack",
    [
        # ('ALLEVIATE'),
        # ('Bioresource'),
        # ('BRAVE'),
        # ('BRICCS'),
        # ('CAE'),
        # ('Cardiomet'),
        # ('CIA'),
        # ('DISCORDANCE'),
        # ('ELASTIC-AS'),
        # ('FAST'),
        # ('GO-DCM'),
        # ('HIC Covid 19'),
        # ('Indapamide'),
        # ('LENTEN'),
        # ('LIMb'),
        # ('MERMAID'),
        # ('PREDICT'),
        # ('Pre-Eclampsia'),
        # ('SCAD'),
        ('SPIRAL', 'SpiralPack'),
    ],
)
def test__setup__studies(client, faker, study, type):
    create_base_data()

    s = Study.query.filter_by(name=study)
    assert LabelPack.query.filter_by(study_id=s.id, type=type).one_or_none() is not None

