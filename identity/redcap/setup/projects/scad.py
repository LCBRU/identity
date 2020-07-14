from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


SCAD_CLINICAL_VISIT = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'SCAD',
            'projects': [28],
        },
    ],

    'recruitment_date_column_name': 'int_date',
    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': 'withdrawal_date',
    'withdrawn_from_study_column_name': 'withdrawal_date',
    'withdrawn_from_study_values': '<isnotnull>',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'complete_or_expected_column_name': 'study_status',
    'complete_or_expected_values': ['<isnull>', '1'],

    'identity_map': {
        ParticipantIdentifierType.__SCAD_REG_ID__: 'scadreg_id',
        ParticipantIdentifierType.__SCAD_ID__: 'scad_id',
        ParticipantIdentifierType.__SCAD_LOCAL_ID__: 'scad_local_id',
    }
}


SCAD_CLINICAL_VISIT_V2 = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'SCAD',
            'projects': [77],
        },
        {
            'instance': 'UHL HSCN',
            'study': 'SCAD',
            'projects': [68],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    **STANDARD_WITHDRAWAL,

    'complete_or_expected_column_name': 'study_status',
    'complete_or_expected_values': ['1'],

    'identity_map': {
        ParticipantIdentifierType.__SCAD_ID__: 'record',
        ParticipantIdentifierType.__SCAD_REG_ID__: 'scadreg_id',
    }
}


SCAD_REGISTRY = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'SCAD',
            'projects': [31],
        },
    ],

    'recruitment_date_column_name': 'scad_reg_date',
    'first_name_column_name': 'frst_nm',
    'last_name_column_name': 'lst_nm',
    'postcode_column_name': 'addrss_pstcd',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__SCAD_REG_ID__: 'record_id',
    }
}


SCAD_SURVEY = {
    'crfs': [
        {
            'instance': 'UoL Survey',
            'study': 'SCAD',
            'projects': [12],
        },
    ],

    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'address_postcode',
    'birth_date_column_name': 'mayo_dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__SCAD_SURVEY_ID__: 'record',
    }
}


SCAD_SURVEY_2016 = {
    'crfs': [
        {
            'instance': 'UoL Survey',
            'study': 'SCAD',
            'projects': [13],
        },
    ],

    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'address_postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__SCAD_REG_ID__: 'scad_reg_id',
    }
}
