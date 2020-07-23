from identity.redcap.setup.standard import SEX_MAP_1M2F_GENDER
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.DESMOND,
            'projects': [19],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'surname',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'birthdate',

    **SEX_MAP_1M2F_GENDER,

    'withdrawal_date_column_name': 'wthdrw_date',
    'withdrawn_from_study_column_name': 'wthdrw_date',
    'withdrawn_from_study_values': ['<isnotnull>'],

    'complete_or_expected_column_name': 'withdrawal_date',
    'complete_or_expected_values': ['<isnotnull>'],

    'post_withdrawal_keep_samples_column_name': 'withdrawal_type',
    'post_withdrawal_keep_samples_values': ['<isnull>', '2', '3'],

    'post_withdrawal_keep_data_column_name': 'withdrawal_type',
    'post_withdrawal_keep_data_values': ['<isnull>', '2', '3'],

    'identity_map': {
        ParticipantIdentifierTypeName.DESMOND_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_no',
    }
})
