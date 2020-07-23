from identity.redcap.setup.standard import SEX_MAP_1M2F_GENDER
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.HAD,
            'projects': [23],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': 'withdrawal_date',
    'withdrawn_from_study_column_name': 'withdrawal_date',
    'withdrawn_from_study_values': ['<isnotnull>'],

    **SEX_MAP_1M2F_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.HAD_ID: 'record',
    }
})
