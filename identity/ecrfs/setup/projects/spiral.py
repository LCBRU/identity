from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_DEMOGRAPHICS, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.ecrfs.setup import crfs, EcrfDefinition


crfs.extend([
    EcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.SPIRAL,
            'projects': [68],
        },
    ],

    **STANDARD_DEMOGRAPHICS,

    'identity_map': {
        ParticipantIdentifierTypeName.SPIRAL_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
    }),
    EcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.SPIRAL,
            'projects': [69],
        },
    ],

    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,
    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.SPIRAL_ID: 'record',
    }
})])
