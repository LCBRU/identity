from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName


PHOSP_COVID19 = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.PHOSP_COVID19,
            'projects': [44],
        },
    ],

    'recruitment_date_column_name': 'crf1a_date',
    'postcode_column_name': 'crf1a_postcode',
    'birth_date_column_name': 'crf1a_date_of_birth',

    'sex_column_name': 'crf1a_sex',
    'sex_column_map': {
        'M': 'M', # Male
        'F': 'F', # Female
        'NK': 'NK', # Not Known
    },

    'identity_map': {
        ParticipantIdentifierTypeName.PHOSP_COVID19_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_num',
        ParticipantIdentifierTypeName.CHI_NUMBER: 'chi_num',
        ParticipantIdentifierTypeName.HC_NUMBER: 'hc_num',
    }
}
