from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


LENTEN = {
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
        ParticipantIdentifierType.__LENTEN_ID__: 'record',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_number',
    }
}
