from identity.ecrfs.setup.standard import SEX_MAP_1M2F_GENDER
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.PARC,
            'projects': [28],
        },
    ],

    'recruitment_date_column_name': 'visit_date',
    'birth_date_column_name': 'date_of_birth',

    'withdrawn_from_study_column_name': 'outcome_withdrawn_trial',
    'withdrawn_from_study_values': ['1'],

    **SEX_MAP_1M2F_GENDER,

    'complete_or_expected_column_name': 'outcome_completed_trial',
    'complete_or_expected_values': ['<isnull>', '1'],

    'identity_map': {
        ParticipantIdentifierTypeName.PARC_ID: 'record',
    }
})
