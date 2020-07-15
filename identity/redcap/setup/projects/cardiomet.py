from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


CARDIOMET = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.CARDIOMET,
            'projects': [67],
        },
    ],

    'recruitment_date_column_name': 'v1_visit_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'complete_or_expected_column_name': 'study_status',
    'complete_or_expected_values': ['1'],

    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierType.__CARDIOMET_ID__: 'record',
    }
}


CARDIOMET_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.CARDIOMET,
            'projects': [64],
        },
    ],

    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__CARDIOMET_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_no',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_no',
    }
}
