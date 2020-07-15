from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


PREDICT = {
    'crf': {
        'PREDICT': {
            'study': StudyName.PREDICT,
            'instance': 'UHL Live',
            'project_id': 62,
        },
    },

    'recruitment_date_column_name': 'date_of_visit',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    **STANDARD_STATUS,

    **STANDARD_WITHDRAWAL,

    'excluded_from_analysis_column_name': 'inc_in_eos_analysis',
    'excluded_from_analysis_values': ['0'],

    'identity_map': {
        ParticipantIdentifierType.__PREDICT_ID__: 'record',
    }
}


PREDICT_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'PREDICT',
            'projects': [63],
        },
    ],

    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__PREDICT_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_no',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_no',
    }
}


PREDICT_REPRODUCIBILITY = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'PREDICT',
            'projects': [76],
        },
    ],

    'recruitment_date_column_name': 'visit_date',

    'identity_map': {
        ParticipantIdentifierType.__PREDICT_ID__: 'predict_id',
    }
}
