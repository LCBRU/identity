from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import SEX_MAP_0F1M, SEX_MAP_0F1M_GENDER
from identity.redcap.setup import crfs

# Need to check with Sue

crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.EDEN,
            'projects': [74],
        },
    ],

    'recruitment_date_column_name': 'date_first_visit',

    **SEX_MAP_0F1M_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.EDEN_ID: 'patient_id',
    }
})


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.EDEN,
            'projects': [63, 66],
        },
    ],

    'recruitment_date_column_name': 'date_first_visit',

    'sex_column_name': 'gender_pat1',
    **SEX_MAP_0F1M,

    'identity_map': {
        ParticipantIdentifierTypeName.EDEN_ID: 'patient_id_pat1',
    }
})
