from identity.setup.studies import StudyName
from flask_login import current_user
from identity.model.id import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    PRINTER_CVRC_LAB_SAMPLE,
    LabelPack,
)
from .printing_methods import print_barcode


ID_TYPE_PARTICIPANT = "SpPt"


class SpiralIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.SPIRAL,
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'SPIRAL Participants'},
            ],
        )


class SpiralPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'SpiralPack',
    }

    __study_name__ = StudyName.SPIRAL

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id().barcode

        self.save_participant_id(participant_id)

        print_barcode(
            printer=PRINTER_CVRC_LAB_SAMPLE,
            barcode=participant_id,
            count=5,
        )
