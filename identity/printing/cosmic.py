from identity.setup.studies import StudyName
from flask_login import current_user
from identity.model.id import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    PRINTER_TMF_BAG,
    PRINTER_TMF_SAMPLE,
    SampleContext,
    BagContext,
    LabelPack,
)
from .printing_methods import (
    print_sample,
    print_bag,
    print_barcode,
)


ID_TYPE_PARTICIPANT = "CosPt"
ID_TYPE_SAMPLE = "CosSa"


class CosmicIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.COSMIC,
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'COSMIC Participants'},
                {ID_TYPE_SAMPLE: 'COSMIC Samples'},
            ],
        )


class CosmicPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'CosmicPack',
    }

    __study_name__ = StudyName.COSMIC

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        self.save_participant_id(participant_id)

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar='COSMIC',
        )

        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        print_bag(
            label_context=bag_context,
            title='COSMIC Samples',
            version='v1.0',
            subheaders=[
                '1 x 8.5ml Serum',
                '1 x 10ml EDTA',
                '1 x 3.5ml Citrate',
            ],
            warnings=['STORE ON ICE', 'Transfer to lab within 90 minutes']
        )
        print_sample(
            label_context=sample_context,
            title='8.5ml Serum'
        )
        print_sample(
            label_context=sample_context,
            title='10ml EDTA'
        )
        print_sample(
            label_context=sample_context,
            title='3.5ml Citrate'
        )

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=participant_id,
            count=5,
        )
