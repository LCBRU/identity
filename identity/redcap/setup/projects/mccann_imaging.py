from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


MCCANN_IMAGING = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.MCCANN_IMAGING,
            'projects': [103],
        },
    ],

    'recruitment_date_column_name': 'mri_date',

    'identity_map': {
        ParticipantIdentifierType.__MCCANN_IMAGE_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_no',
    }
}
