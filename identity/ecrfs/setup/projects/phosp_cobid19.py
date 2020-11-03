from identity.ecrfs.setup.standard import SEX_MAP_MMFF
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs, EcrfDefinition

crfs.extend([
    EcrfDefinition({
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
    **SEX_MAP_MMFF,

    'identity_map': {
        ParticipantIdentifierTypeName.PHOSP_COVID19_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_num',
        ParticipantIdentifierTypeName.CHI_NUMBER: 'chi_num',
        ParticipantIdentifierTypeName.HC_NUMBER: 'hc_num',
    }
})])
