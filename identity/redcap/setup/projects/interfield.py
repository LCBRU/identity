from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_DEMOGRAPHICS
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.INTERFIELD,
            'projects': [104],
        },
    ],

    'recruitment_date_column_name': 'visit_date',

    **SEX_MAP_0F1M_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.INTERFIELD_ID: 'record',
    }
})


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.INTERFIELD,
            'projects': [105],
        },
    ],


    **STANDARD_DEMOGRAPHICS,

    'identity_map': {
        ParticipantIdentifierTypeName.INTERFIELD_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
})
