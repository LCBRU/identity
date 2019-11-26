from ..model import BioresourceIdProvider
from .model import (
    print_sample,
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    LabelPack,
)


class BioresourcePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'BioresourcePack',
    }

    __study_name__ = 'Bioresource'

    def print(self):
        print_sample(label_context=SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=BioresourceIdProvider.query.filter_by(prefix='BR').first(),
        ))
