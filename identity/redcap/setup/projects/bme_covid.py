from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


BME_COVID = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.BME_COVID,
            'projects': [40],
        },
    ],

    'sex_column_name': 'd4_sex',
    'sex_column_map': {
        '2': 'F', # Female
        '1': 'M', # Male
        '3': 'I', # Intersex
        '4': 'NB', # Non-Binary
        '5': 'P', # Prefer not to say
    },

    'identity_map': {
        ParticipantIdentifierType.__BME_COVID_ID__: 'record',
    }
}
