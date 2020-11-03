from identity.ecrfs.setup.standard import SEX_MAP_1M2F_GENDER
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs, RedCapEcrfDefinition

crfs.extend([
    RedCapEcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.COHERE,
            'projects': [22],
        },
    ],

    'recruitment_date_column_name': 'assessment_date_bl',
    'birth_date_column_name': 'dob',

    'withdrawn_from_study_column_name': 'cot_outcome',
    'withdrawn_from_study_values': ['2'],

    **SEX_MAP_1M2F_GENDER,

    'complete_or_expected_column_name': 'cot_outcome',
    'complete_or_expected_values': ['<isnull>', '1'],

    'identity_map': {
        ParticipantIdentifierTypeName.COHERE_ID: 'record',
    }
})])
