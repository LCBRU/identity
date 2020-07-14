from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


MEL = {
    'crfs': [
        {
            'instance': 'UoL Survey',
            'study': 'MEL',
            'projects': [25],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'first_name_column_name': 'forename',
    'last_name_column_name': 'surname',
    'postcode_column_name': 'address_postcode',
    'birth_date_column_name': 'date_of_birth',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '2': 'F', # Female
        '1': 'M', # Male
        '3': 'N', # Prefer not to say
        '4': 'O', # Other
    },

    'identity_map': {
        ParticipantIdentifierType.__MEL_ID__: 'record',
        ParticipantIdentifierType._NHS_NUMBER__: 'nhs_no',
    }
}
