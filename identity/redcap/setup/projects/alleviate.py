from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


ALLEVIATE = {
    'crf': [
        {
            'study': StudyName.ALLEVIATE,
            'instance': REDCapInstance.UHL_LIVE,
            'projects': [98],
        },
        {
            'study': StudyName.ALLEVIATE,
            'instance': REDCapInstance.UOL_CRF,
            'projects': [45],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'excluded_from_analysis_column_name': 'inc_in_eos_analysis',
    'excluded_from_analysis_values': ['0'],

    'identity_map': {
        ParticipantIdentifierType.__ALLEVIATE_ID__: 'record',
    }
}


ALLEVIATE_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': REDCapInstance.UOL_CRF,
            'study': StudyName.ALLEVIATE,
            'projects': [46],
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
        ParticipantIdentifierType.__ALLEVIATE_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_no',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_no',
    }
}
