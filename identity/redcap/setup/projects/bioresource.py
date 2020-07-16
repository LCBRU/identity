from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_STATUS, STANDARD_WITHDRAWAL


BIORESOURCE = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.Bioresource,
            'projects': [9],
        },
    ],

    'recruitment_date_column_name': 'date_of_sig',
    'birth_date_column_name': 'date_of_birth',

    'sex_column_name': 'gender',
    'sex_column_map': {
        '1': 'M',
        '2': 'F',
        '0': 'N',
    },

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.BIORESOURCE_ID: 'record',
    }
}
