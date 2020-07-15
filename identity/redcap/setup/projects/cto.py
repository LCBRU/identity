from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP
from identity.model.id import ParticipantIdentifierType


CTO = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.CTO,
            'projects': [51],
        },
        {
            'instance': REDCapInstance.UOL_CRF,
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
        ParticipantIdentifierType.__CTO_ID__: 'record',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 'hospital_num',
        ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_num',
    }
}
