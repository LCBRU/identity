from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.etl.setup.standard import SEX_MAP_1M2F_GENDER, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.etl.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.Bioresource,
            'projects': [9],
        },
    ],

    'recruitment_date_column_name': 'date_of_sig',
    'birth_date_column_name': 'date_of_birth',

    **SEX_MAP_1M2F_GENDER,

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.BIORESOURCE_ID: 'record',
    }
})
