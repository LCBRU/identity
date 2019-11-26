from ..model import PseudoRandomIdProvider
from .model import (
    print_sample,
    PRINTER_CVRC_LAB_SAMPLE,
    SampleContext,
    LabelPack,
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
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix='SpPt').first(),
            ),
            count=5,
        )
