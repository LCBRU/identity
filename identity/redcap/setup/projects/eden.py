from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP


# Need to check with Sue

EDEN_STP = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.EDEN,
            'projects': [74],
        },
    ],

    'recruitment_date_column_name': 'date_first_visit',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierTypeName.EDEN_ID: 'patient_id',
    }
}


EDEN_STP = {
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.EDEN,
            'projects': [63, 66],
        },
    ],

    'recruitment_date_column_name': 'date_first_visit',

    'sex_column_name': 'gender_pat1',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierTypeName.EDEN_ID: 'patient_id_pat1',
    }
}
