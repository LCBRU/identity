from identity.setup.studies import StudyName
from flask_login import current_user
from identity.model.id import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    PRINTER_BRU_CRF_BAG,
    PRINTER_BRU_CRF_SAMPLE,
    BagContext,
    SampleContext,
    LabelPack,
)
from .printing_methods import (
    print_sample,
    print_bag,
    print_barcode,
)


ID_TYPE_PARTICIPANT = "IndPt"
ID_TYPE_SAMPLE = "IndSa"


class IndapamideIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.Indapamide,
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'Indapamide Participants'},
                {ID_TYPE_SAMPLE: 'Indapamide Samples'},
            ],
        )


class IndapamidePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'IndapamidePack',
    }

    __study_name__ = StudyName.Indapamide

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix="IndPt").first()
        participant_id = participant_id_provider.allocate_id().barcode

        self.save_participant_id(participant_id)

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='Indapamide',
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix="IndSa").first(),
        )

        self.print_visit(bag_context, sample_context, 'Baseline')
        self.print_visit(bag_context, sample_context, '2 Weeks')
        self.print_visit(bag_context, sample_context, '6 Weeks')
        self.print_visit(bag_context, sample_context, '10 Weeks')

        print_barcode(
            printer=PRINTER_BRU_CRF_SAMPLE,
            barcode=participant_id,
            count=4,
        )

    def print_visit(self, bag_context, sample_context, subset):

        print_bag(
            label_context=bag_context,
            title='Indapamide EDTA Bag',
            subset=subset,
            version='v3.0',
            subheaders=['2 x 7.5ml EDTA'],
            lines=['Fill EDTA bottles 3rd & 4th'],
            warnings=[
                'PUT ON ICE',
                'Transfer to lab within 90 minutes'
            ]
        )
        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title='7.5ml EDTA'
            )

        print_bag(
            label_context=bag_context,
            title='Indapamide Serum Bag',
            subset=subset,
            version='v3.0',
            subheaders=['2 x 4.9ml Serum'],
            lines=['Fill Serum bottles 1st & 2nd'],
            warnings=['KEEP AT ROOM TEMPERATURE']
        )
        print_sample(
            label_context=sample_context,
            title='7.5ml Serum'
        )

        print_bag(
            label_context=bag_context,
            title='Indapamide Urine Bag',
            subset=subset,
            version='v3.0',
            subheaders=['1 x 50ml Urine'],
            warnings=['PUT ON ICE']
        )
        print_sample(
            label_context=sample_context,
            title='50ml Urine on ice'
        )
