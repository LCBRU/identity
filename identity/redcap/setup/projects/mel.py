from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName


MEL = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.MEL,
            'projects': [25],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'first_name_column_name': 'forename',
    'last_name_column_name': 'surname',
    'postcode_column_name': 'address_postcode',
    'birth_date_column_name': 'date_of_birth',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '2': 'F', # Female
        '1': 'M', # Male
        '3': 'N', # Prefer not to say
        '4': 'O', # Other
    },

    'identity_map': {
        ParticipantIdentifierTypeName.MEL_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
    }
}
