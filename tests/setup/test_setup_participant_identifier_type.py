from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.model.id import ParticipantIdentifierType
import pytest
from identity.setup import create_base_data


@pytest.mark.parametrize(
    "id_name",
    [
        (ParticipantIdentifierTypeName.STUDY_PARTICIPANT_ID),
        (ParticipantIdentifierTypeName.ALLEVIATE_ID),
        (ParticipantIdentifierTypeName.AS_PROGRESSION_ID),
        (ParticipantIdentifierTypeName.BME_COVID_ID),
        (ParticipantIdentifierTypeName.BREATHE_DEEP_ID),
        (ParticipantIdentifierTypeName.BREATHLESSNESS_ID),
        (ParticipantIdentifierTypeName.BRICCS_ID),
        (ParticipantIdentifierTypeName.CARDIOMET_ID),
        (ParticipantIdentifierTypeName.CARMER_BREATH_ID),
        (ParticipantIdentifierTypeName.CHABLIS_ID),
        (ParticipantIdentifierTypeName.CIA_ID),
        (ParticipantIdentifierTypeName.COHERE_ID),
        (ParticipantIdentifierTypeName.COPD_COVID_19_ID),
        (ParticipantIdentifierTypeName.COPD_INTRO_ID),
        (ParticipantIdentifierTypeName.CTO_ID),
        (ParticipantIdentifierTypeName.CVLPRIT_ID),
        (ParticipantIdentifierTypeName.CVLPRIT_LOCAL_ID),
        (ParticipantIdentifierTypeName.PILOT_ID),
        (ParticipantIdentifierTypeName.DAL_GENE_ID),
        (ParticipantIdentifierTypeName.DESMOND_ID),
        (ParticipantIdentifierTypeName.DHF_ID),
        (ParticipantIdentifierTypeName.DISCORDANCE_ID),
        (ParticipantIdentifierTypeName.DREAM_ID),
        (ParticipantIdentifierTypeName.EASY_AS_ID),
        (ParticipantIdentifierTypeName.EDEN_ID),
        (ParticipantIdentifierTypeName.EDIFY_ID),
        (ParticipantIdentifierTypeName.ELASTIC_AS_ID),
        (ParticipantIdentifierTypeName.EPIGENE1_ID),
        (ParticipantIdentifierTypeName.MEIRU_ID),
        (ParticipantIdentifierTypeName.EXTEND_ID),
        (ParticipantIdentifierTypeName.FAST_ID),
        (ParticipantIdentifierTypeName.FOAMI_ID),
        (ParticipantIdentifierTypeName.BIORESOURCE_ID),
        (ParticipantIdentifierTypeName.GENVASC_ID),
        (ParticipantIdentifierTypeName.GLOBAL_VIEWS_ID),
        (ParticipantIdentifierTypeName.GO_DCM_ID),
        (ParticipantIdentifierTypeName.GRAPHIC2_ID),
        (ParticipantIdentifierTypeName.TMAO_ID),
        (ParticipantIdentifierTypeName.BRAVE_ID),
        (ParticipantIdentifierTypeName.NHS_NUMBER),
        (ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER),
        (ParticipantIdentifierTypeName.HAD_ID),
        (ParticipantIdentifierTypeName.IDAPAMIDE_ID),
        (ParticipantIdentifierTypeName.INTERFIELD_ID),
        (ParticipantIdentifierTypeName.LENTEN_ID),
        (ParticipantIdentifierTypeName.LIMB_ID),
        (ParticipantIdentifierTypeName.MARI_ID),
        (ParticipantIdentifierTypeName.MCCANN_IMAGE_ID),
        (ParticipantIdentifierTypeName.MEL_ID),
        (ParticipantIdentifierTypeName.MI_ECMO_ID),
        (ParticipantIdentifierTypeName.MINERVA_ID),
        (ParticipantIdentifierTypeName.MRP_HFPEF_ID),
        (ParticipantIdentifierTypeName.MULTI_MORBID_PRIORITIES_ID),
        (ParticipantIdentifierTypeName.NON_ADHERENCE_ID),
        (ParticipantIdentifierTypeName.NOVO5K_ID),
        (ParticipantIdentifierTypeName.PARC_ID),
        (ParticipantIdentifierTypeName.HC_NUMBER),
        (ParticipantIdentifierTypeName.CHI_NUMBER),
        (ParticipantIdentifierTypeName.PHOSP_COVID19_ID),
        (ParticipantIdentifierTypeName.PREDICT_ID),
        (ParticipantIdentifierTypeName.PREECLAMPSIA_ID),
        (ParticipantIdentifierTypeName.RAPID_NSTEMI_ID),
        (ParticipantIdentifierTypeName.RECHARGE_ID),
        (ParticipantIdentifierTypeName.REST_ID),
        (ParticipantIdentifierTypeName.SALT_ID),
        (ParticipantIdentifierTypeName.SCAD_SURVEY_ID),
        (ParticipantIdentifierTypeName.SCAD_LOCAL_ID),
        (ParticipantIdentifierTypeName.SCAD_ID),
        (ParticipantIdentifierTypeName.SCAD_REG_ID),
        (ParticipantIdentifierTypeName.SCAD_CAE_ID),
        (ParticipantIdentifierTypeName.SKOPE_ID),
        (ParticipantIdentifierTypeName.SPACE_FOR_COPD_ID),
        (ParticipantIdentifierTypeName.SPIRAL_ID),
        (ParticipantIdentifierTypeName.UHL_HCW_COVID_19_ID),
        (ParticipantIdentifierTypeName.UPFOR5_ID),
        (ParticipantIdentifierTypeName.VASCEGENS_ID),
        (ParticipantIdentifierTypeName.YAKULT_ID),
        (ParticipantIdentifierTypeName.YOGA_ID),
        (ParticipantIdentifierTypeName.UHL_NUMBER),
    ],
)
def test__setup__participant_id_type(client, faker, id_name):
    create_base_data()

    assert ParticipantIdentifierType.query.filter_by(name=id_name).one_or_none() is not None
