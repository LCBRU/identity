from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


CHABLIS = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': StudyName.CHABLIS,
            'projects': [49],
        },
    ],

    'recruitment_date_column_name': 'pat_consent_date',

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierType.__CHABLIS_ID__: 'record',
    }
}
