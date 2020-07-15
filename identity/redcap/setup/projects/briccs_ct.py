from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


BRICCS_CT_2ND_ANALYSIS = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.BRICCS_CT,
            'projects': [80],
        },
    ],

    'recruitment_date_column_name': 'ct_date_time_start',

    'identity_map': {
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_number',
    }
}


BRICCS_CT_SCREENING = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.BRICCS_CT,
            'projects': [28],
        },
    ],

    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 'record',
    }
}
