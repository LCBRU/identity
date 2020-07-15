from identity.setup.studies import StudyName
import pytest
from identity.model import Study
from identity.printing.model import LabelPack
from identity.setup import create_base_data


@pytest.mark.parametrize(
    "study, pack",
    [
        (StudyName.ALLEVIATE, 'AlleviatePack'),
        (StudyName.Bioresource, 'BioresourcePack'),
        (StudyName.BRAVE, 'BravePack'),
        (StudyName.BRAVE, 'BraveExternalPack'),
        (StudyName.BRAVE, 'BravePolandPack'),
        (StudyName.BRICCS, 'BriccsPack'),
        (StudyName.BRICCS, 'BriccsKetteringPack'),
        (StudyName.BRICCS, 'BriccsSamplePack'),
        (StudyName.CAE, 'CaePack'),
        (StudyName.CARDIOMET, 'CardiometPack'),
        (StudyName.CIA, 'CiaPack'),
        (StudyName.DISCORDANCE, 'DiscordancePack'),
        (StudyName.ELASTIC_AS, 'ElasticAsPack'),
        (StudyName.FAST, 'FastPack'),
        (StudyName.GO_DCM, 'GoDcmPack'),
        (StudyName.Indapamide, 'IndapamidePack'),
        (StudyName.LENTEN, 'LentenPack'),
        (StudyName.LIMb, 'LimbPack'),
        (StudyName.MERMAID, 'MermaidPack'),
        (StudyName.PREDICT, 'PredictPack'),
        (StudyName.Pre_Eclampsia, 'PreeclampsiaPack'),
        (StudyName.SCAD, 'ScadPack'),
        (StudyName.SCAD, 'ScadBloodOnlyPack'),
        (StudyName.SCAD, 'ScadFamilyPack'),
        (StudyName.SCAD, 'ScadRegistryPack'),
        (StudyName.SPIRAL, 'SpiralPack'),
    ],
)
def test__setup__labelpacks(client, faker, study, pack):
    create_base_data()

    s = Study.query.filter_by(name=study).one_or_none()
    assert LabelPack.query.filter_by(study_id=s.id, type=pack).one_or_none() is not None

