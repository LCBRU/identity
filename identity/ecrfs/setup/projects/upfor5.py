from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_SEX, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.ecrfs.setup import redcap_crfs

redcap_crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.Upfor5,
            'projects': [24],
        },
    ],

    'recruitment_date_column_name': 'consent_date',
    'postcode_column_name': 'postcode',
    'birth_date_column_name': 'birth_date',

    **SEX_MAP_0F1M_SEX,

    'identity_map': {
        ParticipantIdentifierTypeName.UPFOR5_ID: 'record',
    }
})
