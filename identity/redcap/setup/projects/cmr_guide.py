from identity.redcap.setup.standard import STANDARD_DEMOGRAPHICS
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.CMR_Guide,
            'projects': [59],
        },
    ],

    **STANDARD_DEMOGRAPHICS,

    'identity_map': {
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 'record',
    }
})