from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


RECHARGE_CORE = {
    'crfs': [
        {
            'instance': REDCapInstance.UOL_RECHARGE,
            'study': StudyName.RECHARGE,
            'projects': [13],
        },
    ],

    'sex_column_name': 'sex',
    'sex_column_map': {
        '1': 'M', # Male
        '2': 'F',
    },

    'identity_map': {
        ParticipantIdentifierType.__RECHARGE_ID__: 'record',
    }
}


RECHARGE_SITE = {
    'crfs': [
        {
            'instance': REDCapInstance.UOL_RECHARGE,
            'study': StudyName.RECHARGE,
            'projects': [14, 15, 17, 18],
        },
    ],

    'recruitment_date_column_name': 'enrolment_date',
    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': 'withdrawal_date',
    'withdrawn_from_study_column_name': 'withdrawal_date',
    'withdrawn_from_study_values': '<isnotnull>',

    'sex_column_name': 'sex',
    'sex_column_map': {
        '1': 'M', # Male
        '2': 'F', # Female
    },

    'complete_or_expected_column_name': 'completion_status',
    'complete_or_expected_values': ['<isnull>', '1'],

    'identity_map': {
        ParticipantIdentifierType.__RECHARGE_ID__: 'record',
    }
}
