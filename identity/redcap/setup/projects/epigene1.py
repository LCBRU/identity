from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.EPIGENE1,
            'projects': [12],
        },
    ],

    'recruitment_date_column_name': 'date_inf_consent',
    'birth_date_column_name': 'date_birth',

    'withdrawn_from_study_column_name': 'did_not_complete_reason',
    'withdrawn_from_study_values': ['4'],

    'sex_column_name': 'sex',
    **STANDARD_SEX_MAP,
    **STANDARD_STATUS,

    'excluded_from_study_column_name': 'did_not_complete_reason',
    'excluded_from_study_values': ['6'],

    'identity_map': {
        ParticipantIdentifierTypeName.EPIGENE1_ID: 'record',
    }
})
