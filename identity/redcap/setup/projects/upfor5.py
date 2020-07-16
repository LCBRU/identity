from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL


UPFOR5 = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.Upfor5,
            'projects': [24],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'birth_date',

    'sex_column_name': 'sex',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierTypeName.UPFOR5_ID: 'record',
    }
}
