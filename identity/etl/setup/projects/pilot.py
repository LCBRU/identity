from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.etl.setup.standard import SEX_MAP_0F1M_SEX
from identity.etl.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.Pilot,
            'projects': [5],
        },
    ],

    'recruitment_date_column_name': 'date_time_of_admission',

    **SEX_MAP_0F1M_SEX,

    'identity_map': {
        ParticipantIdentifierTypeName.PILOT_ID: 'record',
    }
})
