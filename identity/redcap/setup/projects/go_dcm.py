from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


GO_DCM = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'GO_DCM',
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

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

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
        ParticipantIdentifierType.__GO_DCM_ID__: 'record',
    }
}


GO_DCM_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'GO_DCM',
            'projects': [92],
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
        ParticipantIdentifierType.__GO_DCM_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_no',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_no',
    }
}
