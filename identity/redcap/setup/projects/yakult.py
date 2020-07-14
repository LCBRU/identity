from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


YAKULT = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'YAKULT',
            'projects': [109],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'sex',
    **STANDARD_SEX_MAP,

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierType.__YAKULT_ID__: 'record',
    }
}
