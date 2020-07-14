from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


CIA = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'CIA',
            'projects': [82],
        },
    ],

    'recruitment_date_column_name': 'visit_date',

    **STANDARD_WITHDRAWAL,

    'excluded_from_analysis_column_name': 'inc_in_eos_analysis',
    'excluded_from_analysis_values': ['1'],

    'identity_map': {
        ParticipantIdentifierType.__CIA_ID__: 'record',
    }
}


CIA_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'CIA',
            'projects': [86],
        },
    ],

    'recruitment_date_column_name': 'research_appt_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__CIA_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_no',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_no',
    }
}
