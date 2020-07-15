from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP
from identity.model.id import ParticipantIdentifierType


PILOT = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.Pilot,
            'projects': [5],
        },
    ],

    'recruitment_date_column_name': 'date_time_of_admission',

    'sex_column_name': 'sex',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__PILOT_ID__: 'record',
    }
}
