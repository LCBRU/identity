from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.ecrfs.setup import crfs, EcrfDefinition


crfs.extend([
    EcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.SKOPE,
            'projects': [95],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.SKOPE_ID: 'record',
    }
})])
