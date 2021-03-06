from flask import current_app
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_DEMOGRAPHICS, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.ecrfs.setup import crfs, RedCapEcrfDefinition


crfs.extend([
    RedCapEcrfDefinition({
        'crfs': [
            {
                'study': StudyName.ALLEVIATE,
                'instance': REDCapInstanceDetail.UHL_LIVE,
                'projects': [98],
            },
            {
                'study': StudyName.ALLEVIATE,
                'instance': REDCapInstanceDetail.UOL_CRF,
                'projects': [45],
            },
        ],

        'recruitment_date_column_name': 'consent_date',
        'birth_date_column_name': 'dob',

        **STANDARD_STATUS,
        **STANDARD_WITHDRAWAL,

        **SEX_MAP_0F1M_GENDER,

        'excluded_from_analysis_column_name': 'inc_in_eos_analysis',
        'excluded_from_analysis_values': ['0'],

        'identity_map': {
            ParticipantIdentifierTypeName.ALLEVIATE_ID: 'record',
        }
    }),
    RedCapEcrfDefinition({
        'crfs': [
            {
                'instance': REDCapInstanceDetail.UOL_CRF,
                'study': StudyName.ALLEVIATE,
                'projects': [46],
            },
        ],

        **STANDARD_DEMOGRAPHICS,

        'identity_map': {
            ParticipantIdentifierTypeName.ALLEVIATE_ID: 'record',
            ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
            ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
        }
    })
])
