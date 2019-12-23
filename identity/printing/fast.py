from ..model import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    print_sample,
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    LabelPack,
)


ID_TYPE_PARTICIPANT = "FST"


class FastIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='FAST',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'FAST Participants'},
            ],
        )


class FastPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'FastPack',
    }

    __study_name__ = 'FAST'

    def print(self):
        print_sample(
            label_context=SampleContext(
                printer=PRINTER_BRU_CRF_SAMPLE,
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first(),
            ),
            count=6,
        )
