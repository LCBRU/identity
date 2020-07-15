from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


NON_ADHERENCE = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': StudyName.NON_ADHERENCE,
            'projects': [87],
        },
    ],

    'recruitment_date_column_name': 'visit_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'sex',
    **STANDARD_SEX_MAP,

    **STANDARD_STATUS,

    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierType.__NON_ADHERENCE_ID__: 'record',
    }
}
