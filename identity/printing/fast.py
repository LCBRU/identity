from identity.setup.studies import StudyName
from flask_login import current_user
from identity.model.id import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    LabelPack,
)
from .printing_methods import print_barcode


ID_TYPE_PARTICIPANT = "FST"


class FastIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.FAST,
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'FAST Participants'},
            ],
        )


class FastPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'FastPack',
    }

    __study_name__ = StudyName.FAST

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        self.save_participant_id(participant_id)

        print_barcode(
            printer=PRINTER_BRU_CRF_SAMPLE,
            barcode=participant_id,
            count=6,
        )
