from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.studies import StudyName
from identity.ecrfs.setup import CiviCrmEcrfDefinition, crfs


crfs.extend([
    CiviCrmEcrfDefinition(
        config={
            'crfs': [{
                'name': 'OMICS Register',
                'case_type_id': 14,
                'study': StudyName.OMICS_REGISTER,
                'custom_tables': ['civicrm_value_omics_register_20'],
            }],

        },
        id_config={
            ParticipantIdentifierTypeName.OMICS_REGISTER_ID: 'omics_id_102',
        })
])
