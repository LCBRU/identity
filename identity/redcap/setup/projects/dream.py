from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.DREAM,
            'projects': [8, 22],
        },
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.DREAM,
            'projects': [20, 21, 24],
        },
    ],

    'recruitment_date_column_name': 'date_enrolled',

    'sex_column_name': 'sex',
    'sex_column_map': {
        '1': 'M',
        '2': 'F',
        '3': 'T',
        '4': 'O',
    },

    'withdrawn_from_study_column_name': 'reason_for_participant_rem',
    'withdrawn_from_study_values': ['6'],

    'excluded_from_analysis_column_name': 'inc_in_eos_analysis',
    'excluded_from_analysis_values': [None, '0'],

    'identity_map': {
        ParticipantIdentifierTypeName.DREAM_ID: 'record',
    }
})
