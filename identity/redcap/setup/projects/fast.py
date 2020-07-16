from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS


FAST = {
    'crf': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.FAST,
            'projects': [43],
        },
    ],

    'recruitment_date_column_name': 'date',
    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': 'wthdrwl_date',
    'withdrawn_from_study_column_name': 'wthdrwl_date',
    'withdrawn_from_study_values': '<isnotnull>',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    **STANDARD_STATUS,

    'identity_map': {
        ParticipantIdentifierTypeName.FAST_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_number',
    }
}


FAST_SCREENING = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.FAST,
            'projects': [48],
        },
    ],

    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierTypeName.PILOT_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
    }
}
