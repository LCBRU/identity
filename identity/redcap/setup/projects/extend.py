from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


EXTEND = {
    'crfs': [
        {
            'instance': 'UoL Survey',
            'study': StudyName.EXTEND,
            'projects': [17],
        },
    ],

    'recruitment_date_column_name': 'date',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__EXTEND_ID__: 'record',
        ParticipantIdentifierType.__MEIRU_ID__: 'meiru_study_id',
    }
}


EXTEND_DEMOGRAPHICS = {
    'crfs': [
        {
            'instance': 'UoL Survey',
            'study': StudyName.EXTEND,
            'projects': [18, 21],
        },
    ],

    'recruitment_date_column_name': 'research_appt_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__EXTEND_ID__: 'record',
        ParticipantIdentifierType.__MEIRU_ID__: 'meiru_study_id',
        ParticipantIdentifierType._NHS_NUMBER__: 'nhs_no',
        ParticipantIdentifierType._UHL_SYSTEM_NUMBER__: 's_no',
    }
}
