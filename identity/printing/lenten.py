from flask_login import current_user
from ..model import PseudoRandomIdProvider
from .model import (
    print_sample,
    print_bag,
    print_barcode,
    print_recruited_notice,
    PRINTER_BRU_CRF_BAG,
    PRINTER_BRU_CRF_SAMPLE,
    BagContext,
    SampleContext,
    LabelPack,
)


class LentenPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'LentenPack',
    }

    __study_name__ = 'LENTEN'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix="LenPt").first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='LENTEN',
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix="LenSa").first(),
        )

        self.print_lenten_visit(bag_context, sample_context, 'Visit 1')
        self.print_lenten_visit(bag_context, sample_context, 'Visit 2')
        self.print_lenten_visit(bag_context, sample_context, 'Visit 3')
        self.print_lenten_visit(bag_context, sample_context, 'Visit 4')

        print_barcode(
            printer=PRINTER_BRU_CRF_SAMPLE,
            barcode=participant_id,
            count=8,
        )

        print_recruited_notice(
            printer=PRINTER_BRU_CRF_SAMPLE,
            study_name='LENTEN',
        )


    def print_lenten_visit(self, bag_context, sample_context, subset):
        print_bag(
            label_context=bag_context,
            title='LENTEN EDTA Bag',
            subset=subset,
            version='v3.0',
            subheaders=['2 x 7.5ml EDTA'],
        )
        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title='7.5ml EDTA'
            )

        print_sample(
            label_context=sample_context,
            title='Urine'
        )
