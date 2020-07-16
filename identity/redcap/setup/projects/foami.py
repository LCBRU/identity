from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP


FOAMI = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.FOAMI,
            'projects': [17],
        },
    ],

    'recruitment_date_column_name': 'date_1st_visit',
    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': 'early_wthdrawal_date',
    'withdrawn_from_study_column_name': 'early_wthdrawal_date',
    'withdrawn_from_study_values': '<isnotnull>',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'complete_or_expected_column_name': 'part_completed_trial_yn',
    'complete_or_expected_values': ['<isnull>', '1'],

    'excluded_from_analysis_column_name': 'inc_in_eos_analysis',
    'excluded_from_analysis_values': ['2'],

    'identity_map': {
        ParticipantIdentifierTypeName.FOAMI_ID: 'record',
    }
}


FOAMI_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.FOAMI,
            'projects': [25],
        },
    ],

    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierTypeName.FOAMI_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
}
