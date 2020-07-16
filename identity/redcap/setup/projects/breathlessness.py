from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName


BREATHLESSNESS = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.Breathlessness,
            'projects': [30],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '1': 'M', # Male
        '2': 'F', # Female
        '999': 'M', # Missing
    },

    'identity_map': {
        ParticipantIdentifierTypeName.BREATHLESSNESS_ID: 'record',
    }
}
