from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER, STANDARD_DEMOGRAPHICS, STANDARD_WITHDRAWAL
from identity.ecrfs.setup import crfs, RedCapEcrfDefinition

crfs.extend([
    RedCapEcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.CAE,
            'projects': [71],
        },
    ],

    **STANDARD_DEMOGRAPHICS,

    'identity_map': {
        ParticipantIdentifierTypeName.SCAD_CAE_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_no',
    }
    }),
    RedCapEcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.CAE,
            'projects': [93],
        },
    ],

    'recruitment_date_column_name': 'scad_reg_date',
    'first_name_column_name': 'frst_nm',
    'last_name_column_name': 'lst_nm',
    'postcode_column_name': 'addrss_pstcd',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,

    'identity_map': {
        ParticipantIdentifierTypeName.SCAD_CAE_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
    }
    }),
    RedCapEcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.CAE,
            'projects': [97],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,

    'complete_or_expected_column_name': 'study_status',
    'complete_or_expected_values': ['<isnull>', '1'],

    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.SCAD_CAE_ID: 'record',
    }
})])
