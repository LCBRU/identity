from ..model import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    print_sample,
    PRINTER_CVRC_LAB_SAMPLE,
    SampleContext,
    LabelPack,
)


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

    def print(self):
        print_sample(
            SampleContext(
                printer=PRINTER_CVRC_LAB_SAMPLE,
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first(),
            ),
            count=5,
        )
