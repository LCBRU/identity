from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import redcap_crfs


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.EDIFY,
            'projects': [30],
        },
    ],

    'identity_map': {
        ParticipantIdentifierTypeName.EDIFY_ID: 'h1_record_id',
    }
})
