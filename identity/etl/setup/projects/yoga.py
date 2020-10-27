from identity.etl.setup.standard import SEX_MAP_1M2F_SEX
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName

from identity.etl.setup import crfs

crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_CRF,
            'study': StudyName.YOGA,
            'projects': [29],
        },
    ],

    'recruitment_date_column_name': 'v1_crf_date',
    'postcode_column_name': 'v1_postcode',
    'birth_date_column_name': 'dob',

    **SEX_MAP_1M2F_SEX,

    'identity_map': {
        ParticipantIdentifierTypeName.YOGA_ID: 'record',
    }
})
