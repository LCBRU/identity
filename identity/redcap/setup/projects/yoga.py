from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.model.id import ParticipantIdentifierType


YOGA = {
    'crfs': [
        {
            'instance': REDCapInstance.UOL_CRF,
            'study': StudyName.YOGA,
            'projects': [29],
        },
    ],

    'recruitment_date_column_name': 'v1_crf_date',
    'postcode_column_name': 'v1_postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'sex',
    'sex_column_map': {
        '1': 'M', # Male
        '2': 'F', # Female
        '999': 'M', # Missing
    },

    'identity_map': {
        ParticipantIdentifierType.__YOGA_ID__: 'record',
    }
}
