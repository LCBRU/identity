from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER
from identity.ecrfs.setup import crfs, RedCapEcrfDefinition


crfs.extend([
    RedCapEcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.VasCeGenS,
            'projects': [19],
        },
    ],

    **SEX_MAP_0F1M_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.VASCEGENS_ID: 'record',
    }
})])
