from flask_login import current_user
from identity.model.id import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    PRINTER_LIMB,
    LabelPack,
)
from .printing_methods import (
    print_sample,
    print_bag_small,
    print_barcode,
    print_recruited_notice,
)


ID_TYPE_PARTICIPANT = "LMbPt"
ID_TYPE_SAMPLE = "LMbSa"


class LimbIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='LIMb',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'LIMb Participants'},
                {ID_TYPE_SAMPLE: 'LIMb Samples'},
            ],
        )


class LimbPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'LimbPack',
    }

    __study_name__ = 'LIMb'

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        self.save_participant_id(participant_id)

        sample_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first()
        edta_id = sample_id_provider.allocate_id(current_user).barcode
        serum_id = sample_id_provider.allocate_id(current_user).barcode

        print_bag_small(
            printer=PRINTER_LIMB,
            title='LIMb EDTA Bag',
            line_1='Date:',
            line_2='Time:',
        )
        print_barcode(
            printer=PRINTER_LIMB,
            barcode=edta_id,
            title='9ml EDTA on Ice (Sample)',
        )
        print_barcode(
            printer=PRINTER_LIMB,
            barcode=edta_id,
            title='9ml EDTA on Ice (Study Pack)',
        )

        print_bag_small(
            printer=PRINTER_LIMB,
            title='LIMb Serum Bag',
            line_1='Date:',
            line_2='Time:',
        )
        print_barcode(
            printer=PRINTER_LIMB,
            barcode=serum_id,
            title='7.5ml Serum on Ice (Sample)',
        )
        print_barcode(
            printer=PRINTER_LIMB,
            barcode=serum_id,
            title='7.5ml Serum on Ice (Study Pack)',
        )

        print_recruited_notice(
            printer=PRINTER_LIMB,
            study_name='LIMb',
        )

        print_barcode(
            printer=PRINTER_LIMB,
            barcode=participant_id,
            count=30,
        )
