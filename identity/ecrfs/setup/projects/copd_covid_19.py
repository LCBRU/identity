from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup import crfs, EcrfDefinition

crfs.extend([
    EcrfDefinition({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.COPD_COVID_19,
            'projects': [108],
        },
    ],

    'recruitment_date_column_name': 'consent_date',

    'identity_map': {
        ParticipantIdentifierTypeName.COPD_COVID_19_ID: 'record',
    }
})])
