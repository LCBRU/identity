from flask_login import current_user
from ..model import PseudoRandomIdProvider
from .model import (
    print_sample,
    print_bag,
    PRINTER_TMF_BAG,
    PRINTER_TMF_SAMPLE,
    SampleContext,
    BagContext,
    LabelPack,
)


class PreeclampsiaPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'PreeclampsiaPack',
    }

    __study_name__ = 'Pre-Eclampsia'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix="PePt").first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar='PRE-ECLAMPSIA',
        )

        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix="PeSa").first(),
        )

        print_bag(
            label_context=bag_context,
            title='EDTA Bag',
            version='v3.0',
            subheaders=[
                '3 x 7.5ml EDTA'
            ],
            lines=[
                'Fill EDTA bottles 2nd, 3rd AND 4th',
                'EDTA on ice for 2 minutes',
                'Return to bag then back on ice',
            ],
            warnings=['Transfer to lab within 90 minutes']
        )
        for _ in range(3):
            print_sample(
                label_context=sample_context,
                title='7.5ml EDTA'
            )

        print_bag(
            label_context=bag_context,
            title='Serum & EDTA Bag',
            version='v3.0',
            subheaders=[
                '1 x 7.5ml Serum',
                '1 x 2.7ml EDTA'
            ],
            lines=[
                'FILL Serum bottles 2nd, 3rd AND 4th',
                'EDTA on iCE for 2 minutes',
                'Return to bag then back on ice',
            ],
            warnings=['Transfer to lab within 90 minutes']
        )
        print_sample(
            label_context=sample_context,
            title='7.5ml Serum'
        )
        print_sample(
            label_context=sample_context,
            title='2.7ml EDTA'
        )
