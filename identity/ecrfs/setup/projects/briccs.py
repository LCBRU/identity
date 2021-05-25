from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from identity.ecrfs.setup.standard import SEX_MAP_0F1M_GENDER, SEX_MAP_0F1M_SEX, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.ecrfs.setup import CiviCrmEcrfDefinition, CustomEcrfDefinition, crfs, RedCapEcrfDefinition

crfs.extend([
    RedCapEcrfDefinition({
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

        'active': True,

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
    }),
    CiviCrmEcrfDefinition(
        config={
            'crfs': [{
                'name': 'BRICCS CiviCRM',
                'case_type_id': 6,
                'study': StudyName.BRICCS,
                'custom_tables': ['civicrm_value_briccs_recruitment_data_10'],
            }],

        },
        id_config={
            ParticipantIdentifierTypeName.BRICCS_ID: 'briccs_id_31',
        }),
    CustomEcrfDefinition({
        'crfs': [
            {
                'name': 'BRICCS Onyx',
                'study': StudyName.BRICCS,
                'database_name': 'briccs',
                'data_query': """

                    SELECT
                        p.id AS record,
                        p.*,
                        pav_nhs_number.text_value AS nhs_number,
                        i2.start_date,
                        CONVERT(DATE_FORMAT(i2.end_date, '%Y%m%d%H%i%S'), UNSIGNED) last_update_timestamp
                    FROM participant p
                    JOIN interview i2
                        ON i2.participant_id = p.id
                    LEFT JOIN participant_attribute_value pav_nhs_number
                        ON pav_nhs_number.participant_id = p.id
                        AND pav_nhs_number.attribute_name = 'pat_nhsnumber'
                    ;

                """,
                'most_recent_timestamp_query': """

                    SELECT CONVERT(DATE_FORMAT(MAX(i2.end_date), '%Y%m%d%H%i%S'), UNSIGNED) latest_timestamp
                    FROM interview i2
                    ;

                """,
                'link': ""
            },
        ],

        'recruitment_date_column_name': 'start_date',
        'first_name_column_name': 'first_name',
        'last_name_column_name': 'last_name',
        'birth_date_column_name': 'birth_date',

        **SEX_MAP_0F1M_GENDER,

        **STANDARD_STATUS,
        **STANDARD_WITHDRAWAL,

        'identity_map': {
            ParticipantIdentifierTypeName.BRICCS_ID: 'barcode',
            ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_number',
            ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 'enrollment_id',
        },   
    }),

])
