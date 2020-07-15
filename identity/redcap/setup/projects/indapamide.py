from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


INDAPAMIDE = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.Indapamide,
            'projects': [50],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierType.__IDAPAMIDE_ID__: 'record',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_number',
    }
}


INDAPAMIDE_SCREENING = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.Indapamide,
            'projects': [54],
        },
    ],

    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 'record',
    }
}


INDAPAMIDE_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.Indapamide,
            'projects': [83],
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
        ParticipantIdentifierType.__IDAPAMIDE_ID__: 'record',
        ParticipantIdentifierType._NHS_NUMBER__: 'nhs_no',
        ParticipantIdentifierType._UHL_SYSTEM_NUMBER__: 's_no',
    }
}
