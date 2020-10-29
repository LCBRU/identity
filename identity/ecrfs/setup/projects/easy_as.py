from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.EASY_AS,
            'projects': [43],
        },
    ],

    'recruitment_date_column_name': 'consent_date',

    'identity_map': {
        ParticipantIdentifierTypeName.EASY_AS_ID: 'record',
    }
})
