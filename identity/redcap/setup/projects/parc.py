from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName


PARC = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
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
        ParticipantIdentifierTypeName.PARC_ID: 'record',
    }
}
