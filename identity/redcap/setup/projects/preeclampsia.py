from identity.redcap.setup.standard import STANDARD_SEX_MAP
from identity.model.id import ParticipantIdentifierType


PRE_ECLAMPSIA = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'Pre-Eclampsia',
            'projects': [39],
        },
    ],

    'recruitment_date_column_name': 'visit_date',
    'birth_date_column_name': 'dob',

    'withdrawn_from_study_column_name': 'non_complete_rsn',
    'withdrawn_from_study_values': ['5'],

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'complete_or_expected_column_name': 'study_status',
    'complete_or_expected_values': ['<isnull>', '1'],

    'identity_map': {
        ParticipantIdentifierType.__PREECLAMPSIA_ID__: 'record',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER_ID__: 's_number',
    }
}
