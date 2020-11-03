from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs, RedCapEcrfDefinition


crfs.extend([
    RedCapEcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.UHL_HCW_COVID_19,
            'projects': [110],
        },
    ],

    'recruitment_date_column_name': 'timestamp',

    'identity_map': {
        ParticipantIdentifierTypeName.UHL_HCW_COVID_19_ID: 'record',
    }
})])
