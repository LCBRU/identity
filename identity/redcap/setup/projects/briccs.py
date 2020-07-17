from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.redcap.setup.standard import SEX_MAP_0F1M_GENDER, SEX_MAP_0F1M_SEX, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.redcap.setup import crfs


crfs.append({
    'crfs': [
        {
            'instance': REDCapInstanceDetail.UHL_LIVE,
            'study': StudyName.BRICCS,
            'projects': [24],
        },
        {
            'instance': REDCapInstanceDetail.UHL_HSCN,
            'study': StudyName.BRICCS,
            'projects': [13, 14, 15, 16, 17, 18, 19, 25, 26, 27],
        },
    ],

    'recruitment_date_column_name': 'int_date',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'post_code_column_name': 'address_postcode',
    'birth_date_column_name': 'dob',

    **SEX_MAP_0F1M_GENDER,

    **STANDARD_STATUS,
    **STANDARD_WITHDRAWAL,

    'identity_map': {
        ParticipantIdentifierTypeName.BRICCS_ID: 'record',
        ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_number',
        ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 's_number',
    },
})
