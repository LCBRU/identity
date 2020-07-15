from identity.setup.studies import StudyName
from identity.model.id import ParticipantIdentifierType

EDIFY = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.EDIFY,
            'projects': [30],
        },
    ],

    'identity_map': {
        ParticipantIdentifierType.__EDIFY_ID__: 'h1_record_id',
    }
}
