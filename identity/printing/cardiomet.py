from flask_login import current_user
from ..model import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    print_bag,
    print_barcode,
    print_sample,
    PRINTER_BRU_CRF_SAMPLE,
    PRINTER_BRU_CRF_BAG,
    BagContext,
    SampleContext,
    LabelPack,
)


ID_TYPE_PARTICIPANT = "CarPt"
ID_TYPE_SAMPLE = "CarSa"


class CardiometIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='Cardiomet',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'CARDIOMET Participants'},
                {ID_TYPE_SAMPLE: 'CARDIOMET Samples'},
            ],
        )


class CardiometPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'CardiometPack',
    }

    __study_name__ = 'Cardiomet'

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='CARDIOMET',
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        self.print_cardiomet_bag(
            bag_context=bag_context,
            sample_context=sample_context,
            subset='V1 Aortic Rest',
        )
        self.print_cardiomet_bag(
            bag_context=bag_context,
            sample_context=sample_context,
            subset='V1 CS Rest',
            include_purple_edta=True,
        )
        self.print_cardiomet_bag(
            bag_context=bag_context,
            sample_context=sample_context,
            subset='V1 Aortic Stress',
        )
        self.print_cardiomet_bag(
            bag_context=bag_context,
            sample_context=sample_context,
            subset='V1 CS Stress',
        )
        self.print_cardiomet_bag(
            bag_context=bag_context,
            sample_context=sample_context,
            subset='V2',
            include_purple_edta=True,
        )

        print_barcode(
            printer=PRINTER_BRU_CRF_SAMPLE,
            barcode=participant_id,
            count=8
        )


    def print_cardiomet_bag(
        self,
        bag_context,
        sample_context,
        subset,
        include_purple_edta=False,
    ):

        subheaders=[
            '2 x 4.9ml Serum Gel [BROWN]',
            '9ml EDTA [ORANGE/RED]',
        ]

        if include_purple_edta:
            subheaders += ['2.7ml EDTA [PURPLE]']

        lines=[
            'Serum: CVS Labs biobanking - process and freeze',
            'EDTA: Gently invert. Place on ice. 5x centrifuge within 20 mins',
        ]
        
        print_bag(
            bag_context,
            title='CARDIOMET SAMPLES',
            subset=subset,
            version='v3.0',
            subheaders=subheaders,
            lines=lines,
        )

        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title=subset + ' 4.9ml (Serum - BROWN)'
            )
        print_sample(
            label_context=sample_context,
            title=subset + ' 9ml (EDTA - ORANGE/RED)'
        )
        if include_purple_edta:
            print_sample(
                label_context=sample_context,
                title=subset + ' 2.7ml (EDTA - PURPLE)'
            )
