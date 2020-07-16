from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName


NOVO5K = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.NOVO5K,
            'projects': [70],
        },
    ],

    'identity_map': {
        ParticipantIdentifierTypeName.NOVO5K_ID: 'record',
    }
}
