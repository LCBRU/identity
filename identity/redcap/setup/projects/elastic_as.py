from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP


ELASTIC_AS = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.ELASTIC_AS,
            'projects': [94],
        },
    ],

    'recruitment_date_column_name': 'date_of_visit',
    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': 'notification_withdraw_date',
    'withdrawn_from_study_column_name': 'notification_withdraw_date',
    'withdrawn_from_study_values': ['<isnotnull>'],

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'post_withdrawal_keep_samples_column_name': 'participant_choice',
    'post_withdrawal_keep_samples_values': ['0', '1'],

    'post_withdrawal_keep_data_column_name': 'participant_choice',
    'post_withdrawal_keep_data_values': ['0', '2'],

    'brc_opt_out_column_name': 'participant_choice',
    'brc_opt_out_values': ['4'],

    'identity_map': {
        ParticipantIdentifierTypeName.EASY_AS_ID: 'record',
    }
}


ELASTIC_AS_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.ELASTIC_AS,
            'projects': [96],
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
        ParticipantIdentifierTypeName.ELASTIC_AS_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
}
