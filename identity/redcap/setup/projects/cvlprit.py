from identity.model.id import ParticipantIdentifierType


CVLPRIT = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'CVLPRIT',
            'projects': [23],
        },
    ],

    'sex_column_name': 'sex',
    'sex_column_map': {
        '1': 'M',
        '2': 'F',
    },

    'identity_map': {
        ParticipantIdentifierType.__CVLPRIT_ID__: 'patient_id',
        ParticipantIdentifierType.__CVLPRIT_LOCAL_ID__: 'local_id',
    }   
}
