from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.Global_Views,
            'projects': [37],
        },
    ],

    'identity_map': {
        ParticipantIdentifierTypeName.GLOBAL_VIEWS_ID: 'record',
    }
})
