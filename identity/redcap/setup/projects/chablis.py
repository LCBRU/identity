from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.CHABLIS,
            'projects': [49],
        },
    ],

    'recruitment_date_column_name': 'pat_consent_date',

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.CHABLIS_ID: 'record',
    }
})
