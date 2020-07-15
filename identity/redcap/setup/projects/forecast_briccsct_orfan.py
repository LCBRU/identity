from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


FORECAST_BRICCSCT_ORFAN_SCREENING = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.FORECAST_BRICCSCT_ORFAN_SCREENING,
            'projects': [72],
        },
    ],

    'recruitment_date_column_name': 'date_of_consent',
    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 'record',
        ParticipantIdentifierType.__UHL_NUMBER__: 'uhl_number', # What is This?
    }
}
