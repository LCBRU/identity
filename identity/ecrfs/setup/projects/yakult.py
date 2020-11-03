from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_SEX, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.ecrfs.setup import redcap_crfs


redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.YAKULT,
            'projects': [109],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_SEX,
    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.YAKULT_ID: 'record',
    }
})
