from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


NOVO5K = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.NOVO5K,
            'projects': [70],
        },
    ],

    'identity_map': {
        ParticipantIdentifierType.__NOVO5K_ID__: 'record',
    }
}
