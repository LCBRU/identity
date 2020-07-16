from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL


UHL_HCW_COVID_19 = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.UHL_HCW_COVID_19,
            'projects': [110],
        },
    ],

    'recruitment_date_column_name': 'timestamp',

    'identity_map': {
        ParticipantIdentifierTypeName.UHL_HCW_COVID_19_ID: 'record',
    }
}
