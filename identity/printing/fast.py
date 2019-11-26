from ..model import PseudoRandomIdProvider
from .model import (
    print_sample,
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    LabelPack,
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
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix="FST").first(),
            ),
            count=6,
        )
