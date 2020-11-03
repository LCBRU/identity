from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_STATUS
from identity.ecrfs.setup import crfs, EcrfDefinition

crfs.extend([
    EcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.COPD_INTROL,
            'projects': [41],
        },
    ],

    'recruitment_date_column_name': 'consent_date',

    'withdrawn_from_study_column_name': 'non_complete_rsn',
    'withdrawn_from_study_values': '5',

    **SEX_MAP_0F1M_GENDER,

    **STANDARD_STATUS,

    'identity_map': {
        ParticipantIdentifierTypeName.COPD_INTRO_ID: 'record',
    }
})])
