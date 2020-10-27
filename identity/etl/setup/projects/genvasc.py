from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.etl.setup import crfs


crfs.append({
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
})
