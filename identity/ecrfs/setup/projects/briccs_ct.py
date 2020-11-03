from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import redcap_crfs


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.BRICCS_CT,
            'projects': [80],
        },
    ],

    'recruitment_date_column_name': 'ct_date_time_start',

    'identity_map': {
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_number',
    }
})


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.BRICCS_CT,
            'projects': [81],
        },
    ],

    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 'record',
    }
})
