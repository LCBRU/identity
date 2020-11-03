from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import redcap_crfs


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.MCCANN_IMAGING,
            'projects': [103],
        },
    ],

    'recruitment_date_column_name': 'mri_date',

    'identity_map': {
        ParticipantIdentifierTypeName.MCCANN_IMAGE_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
    }
})
