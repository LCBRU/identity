from identity.model.id import ParticipantIdentifierType


TEMPLATE = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'Study Name',
            'projects': [28],
        },
    ],

    'recruitment_date_column_name': '',
    'first_name_column_name': '',
    'last_name_column_name': '',
    'postcode_column_name': '',
    'birth_date_column_name': '',

    'withdrawal_date_column_name': '',
    'withdrawn_from_study_column_name': '',
    'withdrawn_from_study_values': '',

    'sex_column_name': '',
    'sex_column_map': {},

    'complete_or_expected_column_name': '',
    'complete_or_expected_values': [],

    'post_withdrawal_keep_samples_column_name': '',
    'post_withdrawal_keep_samples_values': [],

    'post_withdrawal_keep_data_column_name': '',
    'post_withdrawal_keep_data_values': [],

    'brc_opt_out_column_name': '',
    'brc_opt_out_values': [],

    'excluded_from_analysis_column_name': '',
    'excluded_from_analysis_values': [],

    'excluded_from_study_column_name': '',
    'excluded_from_study_values': [],

    'identity_map': {
        ParticipantIdentifierType.__PILOT_ID__: 'record',
    }
}
