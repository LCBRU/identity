from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


BREATHLESSNESS = {
    'crfs': [
        {
            'instance': REDCapInstance.UOL_CRF,
            'study': StudyName.Breathlessness,
            'projects': [30],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '1': 'M', # Male
        '2': 'F', # Female
        '999': 'M', # Missing
    },

    'identity_map': {
        ParticipantIdentifierType.__BREATHLESSNESS_ID__: 'record',
    }
}
