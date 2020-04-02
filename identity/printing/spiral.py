from flask_login import current_user
from ..model import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    PRINTER_CVRC_LAB_SAMPLE,
    SampleContext,
    LabelPack,
)
from .printing_methods import print_barcode


ID_TYPE_PARTICIPANT = "SpPt"


class SpiralIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='SPIRAL',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'SPIRAL Participants'},
            ],
        )


class SpiralPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'SpiralPack',
    }

    __study_name__ = 'SPIRAL'

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        self.save_participant_id(participant_id)

        print_barcode(
            printer=PRINTER_CVRC_LAB_SAMPLE,
            barcode=participant_id,
            count=5,
        )
