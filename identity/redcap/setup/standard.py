from identity.model.sex import SexName


STANDARD_STATUS = {
    'complete_or_expected_column_name': 'study_status_comp_yn',
    'complete_or_expected_values': ['<isnull>', '1'],
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


SEX_MAP_0F1M = {
    'sex_column_map': {
        '0': SexName.FEMALE,
        '1': SexName.MALE,
        '9': SexName.NOT_RECORDED
    },
}


SEX_MAP_0F1M_SEX = {
    'sex_column_name': 'sex',
    **SEX_MAP_0F1M,
}


SEX_MAP_0F1M_GENDER = {
    'sex_column_name': 'gender',
    **SEX_MAP_0F1M,
}

SEX_MAP_0M1F = {
    'sex_column_map': {
        '1': SexName.FEMALE,
        '0': SexName.MALE,
        '9': SexName.NOT_RECORDED,
    },
}

SEX_MAP_0M1F_GENDER = {
    'sex_column_name': 'gender',
    **SEX_MAP_0M1F,
}

SEX_MAP_0M1F_SEX = {
    'sex_column_name': 'sex',
    **SEX_MAP_0M1F,
}


SEX_MAP_1M2F = {
    'sex_column_map': {
        '0': SexName.NOT_RECORDED,
        '1': SexName.MALE,
        '2': SexName.FEMALE,
        '3': SexName.PREFER_NOT_TO_SAY,
        '4': SexName.OTHER,
        '999': SexName.NOT_RECORDED,
    },
}


SEX_MAP_1M2F_SEX = {
    'sex_column_name': 'sex',
    **SEX_MAP_1M2F,
}


SEX_MAP_1M2F_GENDER = {
    'sex_column_name': 'gender',
    **SEX_MAP_1M2F,
}


SEX_MAP_MMFF = {
    'sex_column_map': {
        'M': SexName.MALE,
        'F': SexName.FEMALE,
        'NK': SexName.NOT_RECORDED,
    },
}


SEX_MAP_1M2F3T = {
    'sex_column_map': {
        '1': SexName.MALE,
        '2': SexName.FEMALE,
        '3': SexName.TRANSGENDER,
        '4': SexName.OTHER,
        '999': SexName.NOT_RECORDED,
    },
}


SEX_MAP_1M2F3T_SEX = {
    'sex_column_name': 'sex',
    **SEX_MAP_1M2F3T,
}


SEX_MAP_1M2F3I = {
    'sex_column_map': {
        '1': SexName.MALE,
        '2': SexName.FEMALE,
        '3': SexName.INTERSEX,
        '4': SexName.NON_BINARY,
        '5': SexName.PREFER_NOT_TO_SAY,
    },
}


STANDARD_DEMOGRAPHICS = {
    'recruitment_date_column_name': 'research_appt_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,
}
