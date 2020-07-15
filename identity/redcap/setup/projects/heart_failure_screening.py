from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


HEART_FAILURE_SCREENING = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.Heart_Failure_Screening,
            'projects': [60],
        },
    ],

    'recruitment_date_column_name': 'screening_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 'record',
    }
}
