from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import REVERSE_SEX_MAP, STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


SALT = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.SALT,
            'projects': [111],
        },
    ],

    'recruitment_date_column_name': 'visit_date',

    'sex_column_name': 'gender',
    **REVERSE_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__SALT_ID__: 'record',
    }
}
