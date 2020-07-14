from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


SCAD_CAE_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'SCAD CAE',
            'projects': [71],
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
        ParticipantIdentifierType.__SCAD_CAE_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_no',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_no',
    }
}


SCAD_CAE_REGISTRY = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'SCAD CAE',
            'projects': [93],
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
        ParticipantIdentifierType.__SCAD_CAE_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_no',
    }
}


SCAD_CAE_PHASE_2 = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'SCAD CAE',
            'projects': [28],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'complete_or_expected_column_name': 'study_status',
    'complete_or_expected_values': ['<isnull>', '1'],

    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierType.__SCAD_CAE_ID__: 'record',
    }
}
