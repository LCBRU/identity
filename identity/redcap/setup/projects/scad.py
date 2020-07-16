from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_WITHDRAWAL


SCAD_CLINICAL_VISIT = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.SCAD,
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
        ParticipantIdentifierTypeName.SCAD_REG_ID: 'scadreg_id',
        ParticipantIdentifierTypeName.SCAD_ID: 'scad_id',
        ParticipantIdentifierTypeName.SCAD_LOCAL_ID: 'scad_local_id',
    }
}


SCAD_CLINICAL_VISIT_V2 = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.SCAD,
            'projects': [77],
        },
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.SCAD,
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
        ParticipantIdentifierTypeName.SCAD_ID: 'record',
        ParticipantIdentifierTypeName.SCAD_REG_ID: 'scadreg_id',
    }
}


SCAD_REGISTRY = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.SCAD,
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
        ParticipantIdentifierTypeName.SCAD_REG_ID: 'record_id',
    }
}


SCAD_SURVEY = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.SCAD,
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
        ParticipantIdentifierTypeName.SCAD_SURVEY_ID: 'record',
    }
}


SCAD_SURVEY_2016 = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.SCAD,
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
        ParticipantIdentifierTypeName.SCAD_REG_ID: 'scad_reg_id',
    }
}
