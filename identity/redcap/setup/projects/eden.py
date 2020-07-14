from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType

# Need to check with Sue

EDEN_STP = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'EDEN',
            'projects': [74],
        },
    ],

    'recruitment_date_column_name': 'date_first_visit',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__EDEN_ID__: 'patient_id',
    }
}


EDEN_STP = {
    'crfs': [
        {
            'instance': 'UHL HSCN',
            'study': 'EDEN',
            'projects': [63, 66],
        },
    ],

    'recruitment_date_column_name': 'date_first_visit',

    'sex_column_name': 'gender_pat1',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__EDEN_ID__: 'patient_id_pat1',
    }
}
