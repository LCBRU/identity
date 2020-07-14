from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


UPFOR5 = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': 'Upfor5',
            'projects': [24],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'birth_date',

    'sex_column_name': 'sex',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__UPFOR5_ID__: 'record',
    }
}
