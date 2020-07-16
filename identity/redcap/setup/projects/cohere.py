from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


COHERE = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.COHERE,
            'projects': [22],
        },
    ],

    'recruitment_date_column_name': 'assessment_date_bl',
    'birth_date_column_name': 'dob',

    'withdrawn_from_study_column_name': 'cot_outcome',
    'withdrawn_from_study_values': ['2'],

    'sex_column_name': 'gender',
    'sex_column_map': {
        '2': 'F', # Female
        '1': 'M', # Male
    },

    'complete_or_expected_column_name': 'cot_outcome',
    'complete_or_expected_values': ['<isnull>', '1'],

    'identity_map': {
        ParticipantIdentifierType.__COHERE_ID__: 'record',
    }
}
