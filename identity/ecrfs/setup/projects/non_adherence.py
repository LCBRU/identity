from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_SEX, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.ecrfs.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.NON_ADHERENCE,
            'projects': [87],
        },
    ],

    'recruitment_date_column_name': 'visit_date',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_SEX,

    **STANDARD_STATUS,

    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.NON_ADHERENCE_ID: 'record',
    }
})
