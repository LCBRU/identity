from sqlalchemy.log import Identified
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0M1F_GENDER
from identity.ecrfs.setup import redcap_crfs


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.SALT,
            'projects': [111],
        },
    ],

    'recruitment_date_column_name': 'visit_date',

    **SEX_MAP_0M1F_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.SALT_ID: 'record',
    }
})
