from identity.redcap.setup.standard import SEX_MAP_1M2F_SEX
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_RECHARGE,
            'study': StudyName.RECHARGE,
            'projects': [13],
        },
    ],

    **SEX_MAP_1M2F_SEX,

    'identity_map': {
        ParticipantIdentifierTypeName.RECHARGE_ID: 'record',
    }
})


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_RECHARGE,
            'study': StudyName.RECHARGE,
            'projects': [14, 15, 17, 18],
        },
    ],

    'recruitment_date_column_name': 'enrolment_date',
    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': 'withdrawal_date',
    'withdrawn_from_study_column_name': 'withdrawal_date',
    'withdrawn_from_study_values': '<isnotnull>',

    **SEX_MAP_1M2F_SEX,

    'complete_or_expected_column_name': 'completion_status',
    'complete_or_expected_values': ['<isnull>', '1'],

    'identity_map': {
        ParticipantIdentifierTypeName.RECHARGE_ID: 'record',
    }
})
