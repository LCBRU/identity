from identity.ecrfs.setup.standard import SEX_MAP_1M2F_GENDER
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import redcap_crfs


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.Multi_Morbid_Priorities,
            'projects': [38],
        },
    ],

    **SEX_MAP_1M2F_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.MULTI_MORBID_PRIORITIES_ID: 'record',
    }
})
