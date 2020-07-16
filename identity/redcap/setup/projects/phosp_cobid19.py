from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


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
        ParticipantIdentifierType.__PHOSP_COVID19_ID__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_num',
        ParticipantIdentifierType.__CHI_NUMBER__: 'chi_num',
        ParticipantIdentifierType.__HC_NUMBER__: 'hc_num',
    }
}
