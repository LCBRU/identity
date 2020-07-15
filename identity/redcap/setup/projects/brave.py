from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP
from identity.model.id import ParticipantIdentifierType


BRAVE = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.BRAVE,
            'projects': [26, 29],
        },
        {
            'instance': 'UHL HSCN',
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

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'complete_or_expected_column_name': 'criteria_met',
    'complete_or_expected_values': ['1'],

    'post_withdrawal_keep_samples_column_name': 'withd_type',
    'post_withdrawal_keep_samples_values': ['1'],

    'post_withdrawal_keep_data_column_name': 'withd_type',
    'post_withdrawal_keep_data_values': ['1'],

    'identity_map': {
        ParticipantIdentifierType.__BRAVE_ID__: 'record',
        ParticipantIdentifierType.__BRICCS_ID__: 'briccs_id',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_number',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_number',
    }
}
