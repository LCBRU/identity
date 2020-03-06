from ..model import BioresourceIdProvider, StudyIdSpecification
from .model import (
    print_sample,
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    LabelPack,
)

ID_TYPE_PARTICIPANT = "BR"


class BioresourceIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='Bioresource',
            bioresource_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'Bioresource Participants'},
            ],
        )


class BioresourcePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'BioresourcePack',
    }

    __study_name__ = 'Bioresource'


    def _do_print(self):
        print_sample(label_context=SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=BioresourceIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first(),
        ))
