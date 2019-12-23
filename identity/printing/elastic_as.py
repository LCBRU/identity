from flask_login import current_user
from ..model import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    print_sample,
    print_bag,
    print_barcode,
    print_recruited_notice,
    PRINTER_TMF_BAG,
    PRINTER_TMF_SAMPLE,
    BagContext,
    SampleContext,
    LabelPack,
)


ID_TYPE_PARTICIPANT = "EasSa"
ID_TYPE_SAMPLE = "EasPt"


class ElasticAsIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='ELASTIC-AS',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'ELASTIC-AS Participants'},
                {ID_TYPE_SAMPLE: 'ELASTIC-AS Samples'},
            ],
        )


class ElasticAsPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'ElasticAsPack',
    }

    __study_name__ = 'ELASTIC-AS'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar='ELASTIC-AS',
        )

        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        self.print_visit(bag_context, sample_context, 'Visit Baseline')
        self.print_visit(bag_context, sample_context, 'Visit Month 12')

        print_recruited_notice(
            printer=PRINTER_TMF_SAMPLE,
            study_name='ELASTIC-AS',
        )


    def print_visit(self, bag_context, sample_context, subset):
        print_bag(
            label_context=bag_context,
            title='ELASTIC-AS EDTA Bag',
            subset=subset,
            version='v3.0',
            subheaders=['1 x 9.8ml EDTA (pink)'],
            lines=[
                '* Put EDTA on ice for 2 minutes',
                '* Return to bag then put back on ice',
            ],
            warnings=['Transfer to lab within 90 minutes'],
        )
        print_sample(
            label_context=sample_context,
            title='9.8ml EDTA (pink)'
        )

        print_bag(
            label_context=bag_context,
            title='ELASTIC-AS Serum Bag',
            subset=subset,
            version='v3.0',
            subheaders=[
                '2 x 4.9ml Serum (brown)',
                '1 x 2.7ml Whole Blood (purple)',
            ],
            warnings=[
                'DO NOT PUT ON ICE',
                'Transfer to lab within 90 minutes',
            ],
        )
        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title='4.9ml Serum (brown)'
            )

            print_sample(
            label_context=sample_context,
            title='2.7ml Whole Blood (purple)'
        )
