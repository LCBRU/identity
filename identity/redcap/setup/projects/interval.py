from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.INTERVAL,
            'projects': [55],
        },
    ],

    'recruitment_date_column_name': 'date_enrolled',
    'first_name_column_name': 'demographic_firstname',

    'sex_column_name': 'gender',
    'sex_column_map': {},

    'identity_map': {
        ParticipantIdentifierTypeName.BIORESOURCE_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs',
    }
})
