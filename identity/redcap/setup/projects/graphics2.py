from identity.redcap.setup.standard import STANDARD_SEX_MAP
from identity.model.id import ParticipantIdentifierType


GRAPHIC2 = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'GRAPHIC2',
            'projects': [20],
        },
    ],

    'recruitment_date_column_name': 'date_interview',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'excluded_from_analysis_column_name': 'exclude_from_analysis',
    'excluded_from_analysis_values': ['1'],

    'identity_map': {
        ParticipantIdentifierType.__GRAPHICS2_ID__: 'record',
    }
}
