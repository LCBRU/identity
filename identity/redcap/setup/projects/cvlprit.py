from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.CVLPRIT,
            'projects': [23],
        },
    ],

    'sex_column_name': 'sex',
    'sex_column_map': {
        '1': 'M',
        '2': 'F',
    },

    'identity_map': {
        ParticipantIdentifierTypeName.CVLPRIT_ID: 'patient_id',
        ParticipantIdentifierTypeName.CVLPRIT_LOCAL_ID: 'local_id',
    }   
})
