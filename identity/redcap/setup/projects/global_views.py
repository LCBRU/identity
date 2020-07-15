from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


GLOBAL_VIEWS = {
    'crfs': [
        {
            'instance': REDCapInstance.UOL_INTERNET,
            'study': StudyName.Global_Views,
            'projects': [37],
        },
    ],

    'identity_map': {
        ParticipantIdentifierType.__GLOBAL_VIEWS_ID__: 'record',
    }
}
