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
            'study': StudyName.CARMER_BREATH,
            'projects': [40],
        },
    ],

    'recruitment_date_column_name': 'date_of_consent',
    'birth_date_column_name': 'date_of_birth',

    **SEX_MAP_1M2F_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.CARMER_BREATH_ID: 'record',
    }
})])
