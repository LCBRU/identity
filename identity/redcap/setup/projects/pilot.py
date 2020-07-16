from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP


PILOT = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.Pilot,
            'projects': [5],
        },
    ],

    'recruitment_date_column_name': 'date_time_of_admission',

    'sex_column_name': 'sex',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierTypeName.PILOT_ID: 'record',
    }
}
