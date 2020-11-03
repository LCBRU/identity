from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_DEMOGRAPHICS
from identity.ecrfs.setup import crfs, EcrfDefinition

crfs.extend([
    EcrfDefinition({
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

    **SEX_MAP_0F1M_GENDER,

    'post_withdrawal_keep_samples_column_name': 'participant_choice',
    'post_withdrawal_keep_samples_values': ['0', '1'],

    'post_withdrawal_keep_data_column_name': 'participant_choice',
    'post_withdrawal_keep_data_values': ['0', '2'],

    'brc_opt_out_column_name': 'participant_choice',
    'brc_opt_out_values': ['4'],

    'identity_map': {
        ParticipantIdentifierTypeName.ELASTIC_AS_ID: 'record',
    }
    }),
    EcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.ELASTIC_AS,
            'projects': [96],
        },
    ],

    **STANDARD_DEMOGRAPHICS,

    'identity_map': {
        ParticipantIdentifierTypeName.ELASTIC_AS_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
})])
