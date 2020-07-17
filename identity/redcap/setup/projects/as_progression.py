from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.AS_Progression,
            'projects': [37],
        },
    ],

    'recruitment_date_column_name': 'int_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'postcode_column_name': 'address_postcode',
    'birth_date_column_name': 'dob',

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierTypeName.AS_PROGRESSION_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_number',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_number',
    }
})
