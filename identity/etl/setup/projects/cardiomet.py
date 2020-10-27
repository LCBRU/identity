from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.etl.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_DEMOGRAPHICS, STANDARD_WITHDRAWAL
from identity.etl.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.CARDIOMET,
            'projects': [67],
        },
    ],

    'recruitment_date_column_name': 'v1_visit_date',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,

    'complete_or_expected_column_name': 'study_status',
    'complete_or_expected_values': ['1'],

    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.CARDIOMET_ID: 'record',
    }
})


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.CARDIOMET,
            'projects': [64],
        },
    ],

    **STANDARD_DEMOGRAPHICS,

    'identity_map': {
        ParticipantIdentifierTypeName.CARDIOMET_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
})
