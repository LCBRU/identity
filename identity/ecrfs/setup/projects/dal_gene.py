from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs, RedCapEcrfDefinition

crfs.extend([
    RedCapEcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.Dal_Gene,
            'projects': [47],
        },
    ],

    'recruitment_date_column_name': 'date_main_consent',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierTypeName.DAL_GENE_ID: 'record',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_number',
    }
})])
