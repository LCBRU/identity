from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER
from identity.ecrfs.setup import crfs, EcrfDefinition

crfs.extend([
    EcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.MI_ECMO,
            'projects': [14],
        },
    ],

    'birth_date_column_name': 'dob',

    'withdrawal_date_column_name': 'withdrl_date',
    'withdrawn_from_study_column_name': 'withdrl_date',
    'withdrawn_from_study_values': ['<isnotnull>'],

    **SEX_MAP_0F1M_GENDER,

    'complete_or_expected_column_name': 'eos_study_comp_yn',
    'complete_or_expected_values': ['<isnull>', '1'],

    'excluded_from_study_column_name': 'eos_study_not_comp_rsn',
    'excluded_from_study_values': ['5'],

    'identity_map': {
        ParticipantIdentifierTypeName.MI_ECMO_ID: 'record',
    }
})])
