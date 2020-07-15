from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


PARC = {
    'crfs': [
        {
            'instance': REDCapInstance.UOL_INTERNET,
            'study': StudyName.PARC,
            'projects': [28],
        },
    ],

    'recruitment_date_column_name': 'visit_date',
    'birth_date_column_name': 'date_of_birth',

    'withdrawn_from_study_column_name': 'outcome_withdrawn_trial',
    'withdrawn_from_study_values': ['1'],

    'sex_column_name': 'gender',
    'sex_column_map': {
        '2': 'F', # Female
        '1': 'M', # Male
        '999': 'M', # Missing
    },

    'complete_or_expected_column_name': 'outcome_completed_trial',
    'complete_or_expected_values': ['<isnull>', '1'],

    'identity_map': {
        ParticipantIdentifierType.__PARC_ID__: 'record',
    }
}
