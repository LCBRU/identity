from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName


BREATHE_DEEP = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.Breathe_Deep,
            'projects': [43],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '1': 'M', # Male
        '2': 'F', # Female
        '999': 'Missing', # Missing
    },

    'identity_map': {
        ParticipantIdentifierTypeName.PILOT_ID: 'record',
    }
}
