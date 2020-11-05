from identity.setup.civicrm_instances import CiviCrmInstanceDetail
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import CiviCrmEcrfDefinition, crfs, RedCapEcrfDefinition
from identity.model.sex import SexName


crfs.extend([
    RedCapEcrfDefinition({
        'crfs': [
            {
                'instance': REDCapInstanceDetail.UHL_LIVE,
                'study': StudyName.GENVASC,
                'projects': [66],
            },
        ],

        'recruitment_date_column_name': 'recruitment_date',
        'first_name_column_name': 'first_name',
        'last_name_column_name': 'last_name',

        'identity_map': {
            ParticipantIdentifierTypeName.GENVASC_ID: 'genvasc_id',
            ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 'record',
            ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_number',
        }
    }),
    CiviCrmEcrfDefinition(
        config={
            'crfs': [{
                'name': 'GENVASC Enrolments',
                'case_type_id': 3,
                'study': StudyName.GENVASC,
                'custom_tables': ['civicrm_value_genvasc_recruitment_data_5', 'civicrm_value_genvasc_withdrawal_status_8'],
            }],

            'post_withdrawal_keep_samples_column_name': 'withdrawal_status_24',
            'post_withdrawal_keep_samples_values': ['A'],
            'post_withdrawal_keep_data_column_name': 'withdrawal_status_24',
            'post_withdrawal_keep_samples_values': ['A'],
        },
        id_config={
            ParticipantIdentifierTypeName.GENVASC_ID: 'genvasc_id_10',
        })
])
