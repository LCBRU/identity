from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_STATUS


COPD_INTRO = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.COPD_INTROL,
            'projects': [41],
        },
    ],

    'recruitment_date_column_name': 'consent_date',

    'withdrawn_from_study_column_name': 'non_complete_rsn',
    'withdrawn_from_study_values': '5',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '0': 'F', # Female
        '1': 'M', # Male
        '9': 'O', # Other
    },
    **STANDARD_STATUS,

    'identity_map': {
        ParticipantIdentifierTypeName.PILOT_ID: 'record',
    }
}
