from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


COPD_COVID_19 = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'COPD_COVID_19',
            'projects': [108],
        },
    ],

    'recruitment_date_column_name': 'consent_date',

    'identity_map': {
        ParticipantIdentifierType.__COPD_COVID_19_ID__: 'record',
    }
}
