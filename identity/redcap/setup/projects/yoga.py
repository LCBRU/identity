from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


YOGA = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': 'YOGA',
            'projects': [29],
        },
    ],

    'recruitment_date_column_name': 'v1_crf_date',
    'postcode_column_name': 'v1_postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'sex',
    'sex_column_map': {
        '1': 'M', # Male
        '2': 'F', # Female
        '999': 'M', # Missing
    },

    'identity_map': {
        ParticipantIdentifierType.__YOGA_ID__: 'record',
    }
}
