from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import SEX_MAP_0F1M_GENDER, SEX_MAP_0F1M_SEX
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.BRAVE,
            'projects': [26, 29],
        },
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.BRAVE,
            'projects': [28, 37, 54, 56, 59, 60],
        },
    ],

    'recruitment_date_column_name': 'int_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'address_postcode',
    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': 'withd_date',
    'withdrawn_from_study_column_name': 'withd_date',
    'withdrawn_from_study_values': '<isnotnull>',

    **SEX_MAP_0F1M_GENDER,

    'complete_or_expected_column_name': 'criteria_met',
    'complete_or_expected_values': ['1'],

    'post_withdrawal_keep_samples_column_name': 'withd_type',
    'post_withdrawal_keep_samples_values': ['1'],

    'post_withdrawal_keep_data_column_name': 'withd_type',
    'post_withdrawal_keep_data_values': ['1'],

    'identity_map': {
        ParticipantIdentifierTypeName.BRAVE_ID: 'record',
        ParticipantIdentifierTypeName.BRICCS_ID: 'briccs_id',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_number',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_number',
    }
})
