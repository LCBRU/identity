from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP


GRAPHIC2 = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.GRAPHIC2,
            'projects': [20],
        },
    ],

    'recruitment_date_column_name': 'date_interview',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'excluded_from_analysis_column_name': 'exclude_from_analysis',
    'excluded_from_analysis_values': ['1'],

    'identity_map': {
        ParticipantIdentifierTypeName.GRAPHICS2_ID: 'record',
    }
}
