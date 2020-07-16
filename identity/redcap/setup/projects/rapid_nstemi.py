from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName


RAPID_NSTEMI = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.RAPID_NSTEMI,
            'projects': [79],
        },
    ],

    'recruitment_date_column_name': 'mri_date',

    'identity_map': {
        ParticipantIdentifierTypeName.RAPID_NSTEMI_ID: 'record',
    }
}
