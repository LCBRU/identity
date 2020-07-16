from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL


PREDICT = {
    'crf': {
        'PREDICT': {
            'study': StudyName.PREDICT,
            'instance': REDCapInstanceDetail.UHL_LIVE,
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
        ParticipantIdentifierTypeName.PREDICT_ID: 'record',
    }
}


PREDICT_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.PREDICT,
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
        ParticipantIdentifierTypeName.PREDICT_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
}


PREDICT_REPRODUCIBILITY = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.PREDICT,
            'projects': [76],
        },
    ],

    'recruitment_date_column_name': 'visit_date',

    'identity_map': {
        ParticipantIdentifierTypeName.PREDICT_ID: 'predict_id',
    }
}
