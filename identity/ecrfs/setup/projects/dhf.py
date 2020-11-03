from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER
from identity.ecrfs.setup import redcap_crfs


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.DHF,
            'projects': [70],
        },
    ],

    'recruitment_date_column_name': 'visit_date',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.DHF_ID: 'record',
    }
})
