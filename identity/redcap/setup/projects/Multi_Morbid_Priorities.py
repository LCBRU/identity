from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName


MULTI_MOBID_PRIORITIES = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.Multi_Morbid_Priorities,
            'projects': [38],
        },
    ],

    'sex_column_name': 'gender',
    'sex_column_map': {
        '2': 'F', # Female
        '1': 'M', # Male
        '3': 'P', # Prefer not to say
        '4': 'O', # Other
    },

    'identity_map': {
        ParticipantIdentifierTypeName.MULTI_MORBID_PRIORITIES_ID: 'record',
    }
}
