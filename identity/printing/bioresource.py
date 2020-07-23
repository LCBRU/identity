from identity.setup.studies import StudyName
from identity.model.id import BioresourceIdProvider, StudyIdSpecification
from .model import (
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    LabelPack,
)
from .printing_methods import print_sample


ID_TYPE_PARTICIPANT = "BR"


class BioresourceIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.Bioresource,
            bioresource_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'Bioresource Participants'},
            ],
        )


class BioresourcePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'BioresourcePack',
    }

    __study_name__ = StudyName.Bioresource


    def _do_print(self):
        print_sample(label_context=SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=BioresourceIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first(),
        ))
