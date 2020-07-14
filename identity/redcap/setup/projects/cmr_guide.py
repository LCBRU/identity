from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


CMR_GUIDE = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'CIA',
            'projects': [59],
        },
    ],

    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 'record',
    }
}
