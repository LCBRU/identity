from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.GO_DCM,
            'projects': [91],
        },
    ],

    'recruitment_date_column_name': 'date_of_visit',
    'first_name_column_name': '',
    'last_name_column_name': '',
    'postcode_column_name': '',
    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': '',
    'withdrawn_from_study_column_name': '',
    'withdrawn_from_study_values': '',

    **SEX_MAP_0F1M_GENDER,

    **STANDARD_STATUS,

    **STANDARD_WITHDRAWAL,

    'post_withdrawal_keep_samples_column_name': '',
    'post_withdrawal_keep_samples_values': [],

    'post_withdrawal_keep_data_column_name': '',
    'post_withdrawal_keep_data_values': [],

    'brc_opt_out_column_name': '',
    'brc_opt_out_values': [],

    'excluded_from_analysis_column_name': 'inc_in_eos_analysis',
    'excluded_from_analysis_values': ['1'],

    'excluded_from_study_column_name': '',
    'excluded_from_study_values': [],

    'identity_map': {
        ParticipantIdentifierTypeName.GO_DCM_ID: 'record',
    }
})


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.GO_DCM,
            'projects': [92],
        },
    ],

    'recruitment_date_column_name': 'research_appt_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.GO_DCM_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
})
