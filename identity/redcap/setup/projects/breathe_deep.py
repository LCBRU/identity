from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


BREATHE_DEEP = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': StudyName.Breathe_Deep,
            'projects': [43],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '1': 'M', # Male
        '2': 'F', # Female
        '999': 'Missing', # Missing
    },

    'identity_map': {
        ParticipantIdentifierType.__PILOT_ID__: 'record',
    }
}
