from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import SEX_MAP_0F1M_GENDER
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.GRAPHIC2,
            'projects': [20],
        },
    ],

    'recruitment_date_column_name': 'date_interview',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,

    'excluded_from_analysis_column_name': 'exclude_from_analysis',
    'excluded_from_analysis_values': ['1'],

    'identity_map': {
        ParticipantIdentifierTypeName.GRAPHIC2_ID: 'record',
    }
})
