from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.CARMER_BREATH,
            'projects': [40],
        },
    ],

    'recruitment_date_column_name': 'date_of_consent',
    'birth_date_column_name': 'date_of_birth',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '1': 'M', # Male
        '2': 'F', # Male
    },

    'identity_map': {
        ParticipantIdentifierTypeName.CARMER_BREATH_ID: 'record',
    }
})
