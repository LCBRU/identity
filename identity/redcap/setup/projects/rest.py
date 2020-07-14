from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


REST = {
    'crfs': [
        {
            'instance': 'UoL Survey',
            'study': 'REST',
            'projects': [30],
        },
    ],

    'recruitment_date_column_name': 'visit_date',
    'birth_date_column_name': 'dob',

    'withdrawn_from_study_column_name': 'not_complete_reason',
    'withdrawn_from_study_values': ['5'],

    'sex_column_name': 'sex',
    'sex_column_map': {
        '2': 'F', # Female
        '1': 'M', # Male
    },

    'complete_or_expected_column_name': 'did_complete_yn',
    'complete_or_expected_values': ['<isnull>', '1'],

    'excluded_from_study_column_name': 'not_complete_reason',
    'excluded_from_study_values': ['6'],

    'identity_map': {
        ParticipantIdentifierType.__REST_ID__: 'record',
    }
}


REST_UOL = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': 'REST',
            'projects': [44],
        },
    ],

    'recruitment_date_column_name': 'visit_date',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'sex',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__REST_ID__: 'record',
    }
}
