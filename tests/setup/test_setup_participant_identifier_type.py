from identity.model.id import ParticipantIdentifierType
import pytest
from identity.setup import create_base_data


@pytest.mark.parametrize(
    "id_name",
    [
        ('study_participant_id'),
        ('alleviate_id'),
        ('briccs_id'),
        ('cvlprit_id'),
        ('cvlprit_local_id'),
        ('pilot_id'),
        ('dream_id'),
        ('bioresource_id'),
        ('graphic2_id'),
        ('tmao_id'),
        ('brave_id'),
        ('nhs_number'),
        ('uhl_system_number'),
        ('PREDICT_ID'),
        ('PREECLAMPSIA_ID'),
        ('RAPID_NSTEMI_ID'),
        ('RECHARGE_ID'),
        ('REST_ID'),
        ('SALT_ID'),
        ('SCAD_SURVEY_ID'),
        ('SCAD_LOCAL_ID'),
        ('SCAD_ID'),
        ('SCAD_REG_ID'),
        ('SCAD_CAE_ID'),
        ('SKOPE_ID'),
        ('SPACE_FOR_COPD_ID'),
        ('SPIRAL_ID'),
        ('UHL_HCW_COVID_19_ID'),
        ('UPFOR5_ID'),
        ('VASCEGENS_ID'),
        ('yakult_id'),
        ('yoga_id'),
    ],
)
def test__setup__participant_id_type(client, faker, id_name):
    create_base_data()

    assert ParticipantIdentifierType.query.filter_by(name=id_name).one_or_none() is not None

