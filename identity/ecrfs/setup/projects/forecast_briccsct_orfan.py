from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs, RedCapEcrfDefinition

crfs.extend([
    RedCapEcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.FORECAST_BRICCSCT_ORFAN_SCREENING,
            'projects': [72],
        },
    ],

    'recruitment_date_column_name': 'date_of_consent',
    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 'record',
        ParticipantIdentifierTypeName.UHL_NUMBER: 'uhl_number', # What is This?
    }
})])
