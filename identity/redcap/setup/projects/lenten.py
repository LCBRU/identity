from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_WITHDRAWAL
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.LENTEN,
            'projects': [56],
        },
    ],

    'recruitment_date_column_name': 'v1_visit_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'complete_or_expected_column_name': 'study_status',
    'complete_or_expected_values': ['1'],

    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.LENTEN_ID: 'record',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_number',
    }
})
