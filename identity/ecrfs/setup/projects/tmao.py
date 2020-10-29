from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.ecrfs.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.TMAO,
            'projects': [25],
        },
    ],

    'birth_date_column_name': 'tmao_dob',

    'sex_column_name': 'tmao_gender',
    **SEX_MAP_0F1M,

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.TMAO_ID: 'record',
    }
})
