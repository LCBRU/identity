from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import SEX_MAP_0M1F_GENDER
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.MARI,
            'projects': [52],
        },
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.MARI,
            'projects': [16],
        },
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.MARI,
            'projects': [30, 31, 32, 33, 34, 35, 36, 55, 57, 58],
        },
    ],

    'recruitment_date_column_name': 'operation_date',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0M1F_GENDER,

    'excluded_from_analysis_column_name': 'inc_in_eos_analysis',
    'excluded_from_analysis_values': ['0'],

    'identity_map': {
        ParticipantIdentifierTypeName.MARI_ID: 'record',
    }
})
