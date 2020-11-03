from identity.ecrfs.setup.standard import SEX_MAP_1M2F_SEX
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs, EcrfDefinition

crfs.extend([
    EcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.CVLPRIT,
            'projects': [23],
        },
    ],

    **SEX_MAP_1M2F_SEX,

    'identity_map': {
        ParticipantIdentifierTypeName.CVLPRIT_ID: 'patient_id',
        ParticipantIdentifierTypeName.CVLPRIT_LOCAL_ID: 'local_id',
    }
})])
