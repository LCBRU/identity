from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP


CTO = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.CTO,
            'projects': [51],
        },
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.CTO,
            'projects': [15],
        },
    ],

    'first_name_column_name': 'first_name',
    'last_name_column_name': 'surname',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'sex',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierTypeName.CTO_ID: 'record',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 'hospital_num',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_num',
    }
}
