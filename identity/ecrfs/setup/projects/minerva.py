from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER
from identity.ecrfs.setup import redcap_crfs


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.MINERVA,
            'projects': [53],
        },
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.MINERVA,
            'projects': [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 50, 51, 52, 61, 62, 64, 65, 69],
        },
    ],

    'recruitment_date_column_name': 'consent_sign_date_time',
    'birth_date_column_name': 'dob',

    'withdrawn_from_study_column_name': 'withd_study',
    'withdrawn_from_study_values': ['1'],

    **SEX_MAP_0F1M_GENDER,

    'complete_or_expected_column_name': 'comp_study',
    'complete_or_expected_values': ['1'],

    'identity_map': {
        ParticipantIdentifierTypeName.MINERVA_ID: 'record',
    }
})
