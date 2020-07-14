from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS
from identity.model.id import ParticipantIdentifierType


INTERVAL = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'INTERVAL',
            'projects': [55],
        },
    ],

    'recruitment_date_column_name': 'date_enrolled',
    'first_name_column_name': 'demographic_firstname',

    'sex_column_name': 'gender',
    'sex_column_map': {},

    'identity_map': {
        ParticipantIdentifierType.__BIORESOURCE_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs',
    }
}
