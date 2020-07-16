from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


MI_ECMO = {
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

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'complete_or_expected_column_name': 'eos_study_comp_yn',
    'complete_or_expected_values': ['<isnull>', '1'],

    'excluded_from_study_column_name': 'eos_study_not_comp_rsn',
    'excluded_from_study_values': ['5'],

    'identity_map': {
        ParticipantIdentifierType.__MI_ECMO_ID__: 'record',
    }
}
