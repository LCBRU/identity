from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


BRICCS = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.BRICCS,
            'projects': [24],
        },
        {
            'instance': 'UHL HSCN',
            'study': StudyName.BRICCS,
            'projects': [13, 14, 15, 16, 17, 18, 19, 25, 26, 27],
        },
    ],

    'recruitment_date_column_name': 'int_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'post_code_column_name': 'address_postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierType.__BRICCS_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_number',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_number',
    },
}
