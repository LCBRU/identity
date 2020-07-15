from identity.setup.redcap_instances import REDCapInstance
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import REVERSE_SEX_MAP
from identity.model.id import ParticipantIdentifierType


MARI = {
    'crfs': [
        {
            'instance': REDCapInstance.UHL_LIVE,
            'study': StudyName.MARI,
            'projects': [28],
        },
        {
            'instance': REDCapInstance.UOL_CRF,
            'study': StudyName.MARI,
            'projects': [16],
        },
        {
            'instance': REDCapInstance.UHL_HSCN,
            'study': StudyName.MARI,
            'projects': [30, 31, 32, 33, 34, 35, 36, 55, 57, 58],
        },
    ],

    'recruitment_date_column_name': 'operation_date',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **REVERSE_SEX_MAP,

    'excluded_from_analysis_column_name': 'inc_in_eos_analysis',
    'excluded_from_analysis_values': ['0'],

    'identity_map': {
        ParticipantIdentifierType.__MARI_ID__: 'record',
    }
}
