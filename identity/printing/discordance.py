from ..model import PseudoRandomIdProvider
from .model import (
    print_sample,
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    LabelPack,
)


class DiscordancePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'DiscordancePack',
    }

    __study_name__ = 'DISCORDANCE'

    def print(self):
        print_sample(
            label_context=SampleContext(
                printer=PRINTER_BRU_CRF_SAMPLE,
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix="DisPt").first(),
            ),
            count=6,
        )
