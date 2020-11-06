from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.studies import StudyName
from identity.ecrfs.setup import CiviCrmEcrfDefinition, crfs


crfs.extend([
    CiviCrmEcrfDefinition(
        config={
            'crfs': [{
                'name': 'GRAPHIC Enrolment',
                'case_type_id': 5,
                'study': StudyName.GRAPHIC,
                'custom_tables': ['civicrm_value_graphic2_9'],
            }],

        },
        id_config={
            ParticipantIdentifierTypeName.GRAPHIC_ID: 'graphic_participant_id_26',
            ParticipantIdentifierTypeName.GRAPHIC_LAB_ID: 'graphic_lab_id_25',
        })
])
