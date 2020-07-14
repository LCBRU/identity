STANDARD_STATUS = {
    'complete_or_expected_column_name': 'study_status_comp_yn',
    'complete_or_expected_values': [None, '1'],
}


STANDARD_WITHDRAWAL = {
    'withdrawal_date_column_name': 'wthdrw_date',
    'withdrawn_from_study_column_name': 'wthdrw_date',
    'withdrawn_from_study_values': ['<isnotnull>'],

    'post_withdrawal_keep_samples_column_name': 'wthdrwl_optn_chsn',
    'post_withdrawal_keep_samples_values': ['0', '1'],

    'post_withdrawal_keep_data_column_name': 'wthdrwl_optn_chsn',
    'post_withdrawal_keep_data_values': ['0', '2'],

    'brc_opt_out_column_name': 'wthdrwl_optn_chsn',
    'brc_opt_out_values': ['4'],
}


STANDARD_SEX_MAP = {
    'sex_column_map': {
        '0': 'F', # Female
        '1': 'M', # Male
        '9': 'N', # Not Recorded
    },
}


REVERSE_SEX_MAP = {
    'sex_column_map': {
        '1': 'F', # Female
        '0': 'M', # Male
        '9': 'N', # Not Recorded
    },
}
