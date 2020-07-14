from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


DESMOND = {
    'crfs': [
        {
            'instance': 'UoL Survey',
            'study': 'DESMOND',
            'projects': [19],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'surname',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'birthdate',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '2': 'F', # Female
        '1': 'M', # Male
        '3': 'N', # Do not wish to disclose
    },

    'withdrawal_date_column_name': 'wthdrw_date',
    'withdrawn_from_study_column_name': 'wthdrw_date',
    'withdrawn_from_study_values': ['<isnotnull>'],

    'complete_or_expected_column_name': 'withdrawal_date',
    'complete_or_expected_values': ['<isnotnull>'],

    'post_withdrawal_keep_samples_column_name': 'withdrawal_type',
    'post_withdrawal_keep_samples_values': ['<isnull>', '2', '3'],

    'post_withdrawal_keep_data_column_name': 'withdrawal_type',
    'post_withdrawal_keep_data_values': ['<isnull>', '2', '3'],

    'identity_map': {
        ParticipantIdentifierType.__DESMOND_ID__: 'record',
        ParticipantIdentifierType._NHS_NUMBER__: 'nhs_no',
    }
}
