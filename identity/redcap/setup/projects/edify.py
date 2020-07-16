from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.model.id import ParticipantIdentifierType

EDIFY = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.EDIFY,
            'projects': [30],
        },
    ],

    'identity_map': {
        ParticipantIdentifierType.__EDIFY_ID__: 'h1_record_id',
    }
}
