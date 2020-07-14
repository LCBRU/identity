from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


E = {
    'crfs': [
        {
            'instance': 'UoL Survey',
            'study': 'EASY AS',
            'projects': [43],
        },
    ],

    'recruitment_date_column_name': 'consent_date',

    'identity_map': {
        ParticipantIdentifierType.__EASY_AS_ID__: 'record',
    }
}
