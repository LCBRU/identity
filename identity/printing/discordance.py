from ..model import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    print_sample,
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    LabelPack,
)


ID_TYPE_PARTICIPANT = "DisPt"


class AlleviateIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='DISCORDANCE',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'DISCORDANCE Participants'},
            ],
        )


class DiscordancePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'DiscordancePack',
    }

    __study_name__ = 'DISCORDANCE'

    def _do_print(self):
        print_sample(
            label_context=SampleContext(
                printer=PRINTER_BRU_CRF_SAMPLE,
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first(),
            ),
            count=6,
        )
