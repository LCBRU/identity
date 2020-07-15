from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


MULTI_MOBID_PRIORITIES = {
    'crfs': [
        {
            'instance': 'UoL Survey',
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
        ParticipantIdentifierType.__MULTI_MORBID_PRIORITIES_ID__: 'record',
    }
}
