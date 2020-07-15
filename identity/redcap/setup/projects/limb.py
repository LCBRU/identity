from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


LIMB = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': StudyName.LIMb,
            'projects': [31, 32],
        },
    ],

    'recruitment_date_column_name': 'pat_consent_date',

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierType.__LIMB_ID__: 'record',
    }
}


LIMB_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': StudyName.LIMb,
            'projects': [34],
        },
    ],

    'recruitment_date_column_name': 'recruitment_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__LIMB_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_no',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_no',
    }
}


LIMB_SCREENING = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': StudyName.LIMb,
            'projects': [36],
        },
    ],

    'recruitment_date_column_name': 'recruited_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__LIMB_ID__: 'record',
    }
}
