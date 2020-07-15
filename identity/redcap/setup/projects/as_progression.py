from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP
from identity.model.id import ParticipantIdentifierType


AS_PROGRESSION = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.AS_Progression,
            'projects': [37],
        },
    ],

    'recruitment_date_column_name': 'int_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'address_postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__AS_PROGRESSION_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_number',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_number',
    }
}
