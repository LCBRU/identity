from flask_login import current_user
from ..model import LegacyIdProvider, SequentialIdProvider, StudyIdSpecification
from .model import (
    PRINTER_BRU_CRF_SAMPLE,
    PRINTER_BRU_CRF_BAG,
    BagContext,
    SampleContext,
    LabelPack,
)
from .printing_methods import (
    print_aliquot,
    print_bag,
    print_barcode,
    print_sample,
)

ID_NAME_BRICCS_PARTICIPANT='BRICCS Participant Number'
ID_NAME_BRICCS_SAMPLE='BRICCS Sample Number'
ID_NAME_BRICCS_ALIQUOT = 'BRICCS ALIQUOT'
ID_NAME_BRICCS_KETTERING_ALIQUOT = f'KETTERING {ID_NAME_BRICCS_ALIQUOT}'

ID_TYPE_PARTICIPANT = "BPt"
ID_TYPE_SAMPLE = "BSa"


class BriccsIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='BRICCS',
            legacy_identifier_types=[
                {ID_TYPE_PARTICIPANT: ID_NAME_BRICCS_PARTICIPANT},
                {ID_TYPE_SAMPLE: ID_NAME_BRICCS_SAMPLE},
            ],
            sequential_identifier_types=[
                {
                    'name': ID_NAME_BRICCS_KETTERING_ALIQUOT,
                    'last_number': 380,
                },
            ]
        )


class BriccsBags():
    def print_pack(self, study_name, additional_sample_label_count):
        participant_id_provider = LegacyIdProvider.query.filter_by(name=ID_NAME_BRICCS_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar=study_name,
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=LegacyIdProvider.query.filter_by(name=ID_NAME_BRICCS_SAMPLE).first(),
        )

        self.print_citrate_bag(bag_context=bag_context, sample_context=sample_context)
        self.print_serum_bag(bag_context=bag_context, sample_context=sample_context)
        self.print_urine_bag(bag_context=bag_context, sample_context=sample_context)

        for _ in range(additional_sample_label_count):
            print_sample(sample_context)


    def print_serum_bag(
        self,
        bag_context,
        sample_context,
    ):
        print_bag(
            label_context=bag_context,
            title='Serum and EDTA Bag',
            version='v3.0',
            subheaders=[
                '1 x 7.5ml Serum',
                '1 x 2.7ml EDTA',
            ],
            lines=[
                '* Fill serum bottle 1st',
                '* Return to bag',
                '* Fill the 2.7ml EDTA bottle 5th',
                '* Return to bag',
            ],
            warnings=[
                'DO NOT PUT ON ICE',
                'Transfer to lab within 90 minutes',
            ],
        )
        print_sample(
            label_context=sample_context,
            title='2.7ml EDTA'
        )
        print_sample(
            label_context=sample_context,
            title='7.5ml Serum'
        )

    def print_citrate_bag(
        self,
        bag_context,
        sample_context,
    ):
        print_bag(
            label_context=bag_context,
            title='Citrate and EDTA Bag',
            version='v3.0',
            subheaders=[
                '1 x 4.3ml Citrate',
                '2 x 7.5ml EDTA',
            ],
            lines=[
                '* Fill citrate bottle 2nd',
                '* Fill EDTA bottles 3rd and 4th',
                '* Put citrate and EDTA on ice for 2 minutes',
                '* Return to bag then put back on ice',
            ],
            warnings=['Transfer to lab within 90 minutes'],
        )
        print_sample(
            label_context=sample_context,
            title='4.3ml Citrate'
        )
        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title='7.5ml EDTA'
            )

    def print_edta_bag(
        self,
        bag_context,
        sample_context,
    ):
        print_bag(
            label_context=bag_context,
            title='EDTA Bag',
            version='v3.0',
            subheaders=[
                '2 x 7.5ml EDTA',
                '1 x 2.7ml EDTA',
            ],
            warnings=[
                'PUT ON ICE IMMEDIATELY',
                'Start centrifugation within 2 hours',
            ],
        )

        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title='7.5ml EDTA'
            )
        print_sample(
            label_context=sample_context,
            title='2.7ml EDTA'
        )

    def print_urine_bag(
        self,
        bag_context,
        sample_context,
    ):
        print_bag(
            label_context=bag_context,
            title='Urine Bag',
            version='v3.0',
            subheaders=[
                '1 x 25ml plain bottle with EDTA',
            ],
            lines=[
                '* Fill with 25ml MSU/CSU',
                '* Put on ice for 2 minutes then',
                '* Return to bag then put back on ice',
            ],
            warnings=['Transfer to lab within 90 minutes'],
        )
        print_sample(
            label_context=sample_context,
            title='25ml EDTA'
        )


class BriccsPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'BriccsPack',
    }

    __study_name__ = 'BRICCS'

    def _do_print(self):
        bb = BriccsBags()
        bb.print_pack(study_name='BRICCS', additional_sample_label_count=2)


class BriccsKetteringPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'BriccsKetteringPack',
    }

    __study_name__ = 'BRICCS'

    def _do_print(self):
        self.print_pack(
            site_prefix='91',
            site_name='Kettering',
        )

    def print_pack(self, site_prefix, site_name, additional_sample_label_count=0):
        participant_id_provider = LegacyIdProvider.query.filter_by(name=ID_NAME_BRICCS_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='BRICCS ' + site_name,
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=LegacyIdProvider.query.filter_by(name=ID_NAME_BRICCS_SAMPLE).first(),
        )

        bb = BriccsBags()
        bb.print_edta_bag(bag_context=bag_context, sample_context=sample_context)

        print_barcode(
            printer=PRINTER_BRU_CRF_SAMPLE,  
            barcode=participant_id,
            title='Lab log',
        )

        aliquote_id_provider = SequentialIdProvider.query.filter_by(name=site_name.upper() + ' ' + ID_NAME_BRICCS_ALIQUOT).first()
        alliquot_id = aliquote_id_provider.allocate_id(current_user)

        for i in range(8):
            print_aliquot(
                printer=sample_context.sample_printer,
                barcode='p{}{}-{}'.format(
                    site_prefix,
                    alliquot_id.id,
                    i+1,
                )
            )

        print_aliquot(
            printer=sample_context.sample_printer,
            barcode='b{}{}'.format(
                site_prefix,
                alliquot_id.id,
            )
        )

        for _ in range(additional_sample_label_count):
            print_sample(sample_context)


class BriccsSamplePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'BriccsSamplePack',
    }

    __study_name__ = 'BRICCS'

    def _do_print(self):
        print_sample(label_context=SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=LegacyIdProvider.query.filter_by(name=ID_NAME_BRICCS_SAMPLE).first(),
        ))
