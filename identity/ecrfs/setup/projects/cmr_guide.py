from identity.ecrfs.setup.standard import STANDARD_DEMOGRAPHICS
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs, EcrfDefinition

crfs.extend([
    EcrfDefinition({
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
})])
