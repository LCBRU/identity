from identity.ecrfs.setup.standard import SEX_MAP_1M2F_GENDER
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs, EcrfDefinition

crfs.extend([
    EcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.Breathe_Deep,
            'projects': [43],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    **SEX_MAP_1M2F_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.BREATHE_DEEP_ID: 'record',
    }
})])
