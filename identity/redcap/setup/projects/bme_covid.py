from identity.redcap.setup.standard import SEX_MAP_1M2F3I
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UOL_INTERNET,
            'study': StudyName.BME_COVID,
            'projects': [40],
        },
    ],

    'sex_column_name': 'd4_sex',
    **SEX_MAP_1M2F3I,

    'identity_map': {
        ParticipantIdentifierTypeName.BME_COVID_ID: 'record',
    }
})
