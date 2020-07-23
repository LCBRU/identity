from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import SEX_MAP_0F1M_GENDER
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.Pre_Eclampsia,
            'projects': [39],
        },
    ],

    'recruitment_date_column_name': 'visit_date',
    'birth_date_column_name': 'dob',

    'withdrawn_from_study_column_name': 'non_complete_rsn',
    'withdrawn_from_study_values': ['5'],

    **SEX_MAP_0F1M_GENDER,

    'complete_or_expected_column_name': 'study_status',
    'complete_or_expected_values': ['<isnull>', '1'],

    'identity_map': {
        ParticipantIdentifierTypeName.PREECLAMPSIA_ID: 'record',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_number',
    }
})
