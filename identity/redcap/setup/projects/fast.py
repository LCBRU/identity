from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_STATUS
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
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

    **SEX_MAP_0F1M_GENDER,

    **STANDARD_STATUS,

    'identity_map': {
        ParticipantIdentifierTypeName.FAST_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_number',
    }
})


crfs.append({
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
        ParticipantIdentifierTypeName.FAST_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
    }
})
