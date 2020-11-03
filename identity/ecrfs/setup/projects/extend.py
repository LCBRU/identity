from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_DEMOGRAPHICS
from identity.ecrfs.setup import redcap_crfs


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.EXTEND,
            'projects': [17],
        },
    ],

    'recruitment_date_column_name': 'date',

    **SEX_MAP_0F1M_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.EXTEND_ID: 'record',
        ParticipantIdentifierTypeName.MEIRU_ID: 'meiru_study_id',
    }
})


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.EXTEND,
            'projects': [18, 21],
        },
    ],

    **STANDARD_DEMOGRAPHICS,

    'identity_map': {
        ParticipantIdentifierTypeName.EXTEND_ID: 'record',
        ParticipantIdentifierTypeName.MEIRU_ID: 'meiru_study_id',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
})
