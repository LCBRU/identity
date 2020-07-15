from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


GENVASC_DEATH_DATA = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.GENVASC,
            'projects': [66],
        },
    ],

    'recruitment_date_column_name': 'recruitment_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',

    'identity_map': {
        ParticipantIdentifierType.__GENVASC_ID__: 'genvasc_id',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 'record',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_number',
    }
}
