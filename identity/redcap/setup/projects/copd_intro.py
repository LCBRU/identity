from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


COPD_INTRO = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': 'COPD INTROL',
            'projects': [41],
        },
    ],

    'recruitment_date_column_name': 'consent_date',

    'withdrawn_from_study_column_name': 'non_complete_rsn',
    'withdrawn_from_study_values': '5',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '0': 'F', # Female
        '1': 'M', # Male
        '9': 'O', # Other
    },
    **STANDARD_STATUS,

    'identity_map': {
        ParticipantIdentifierType.__PILOT_ID__: 'record',
    }
}
