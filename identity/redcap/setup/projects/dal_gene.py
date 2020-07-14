from identity.model.id import ParticipantIdentifierType


DAL_GENE = {
    'crfs': [
        {
            'instance': 'UHL Live',
            'study': 'Dal-Gene',
            'projects': [47],
        },
    ],

    'recruitment_date_column_name': 'date_main_consent',
    'first_name_column_name': 'first_name',
    'last_name_column_name': 'last_name',
    'birth_date_column_name': 'dob',

    'identity_map': {
        ParticipantIdentifierType.__DAL_GENE_ID__: 'record',
        ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_number',
    }
}
