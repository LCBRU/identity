from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


RAPID_NSTEMI = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'RAPID_NSTEMI',
            'projects': [79],
        },
    ],

    'recruitment_date_column_name': 'mri_date',

    'identity_map': {
        ParticipantIdentifierType.__RAPID_NSTEMI_ID__: 'record',
    }
}
