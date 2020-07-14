from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


TMAO = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'TMAO',
            'projects': [25],
        },
    ],

    'birth_date_column_name': 'tmao_dob',

    'sex_column_name': 'tmao_gender',
    **STANDARD_SEX_MAP,

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierType.__TMAO_ID__: 'record',
    }
}
