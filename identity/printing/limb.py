from flask_login import current_user
from ..model import PseudoRandomIdProvider
from .model import (
    print_sample,
    print_bag_small,
    print_barcode,
    print_recruited_notice,
    PRINTER_LIMB,
    LabelPack,
)


class LimbPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'LimbPack',
    }

    __study_name__ = 'LIMb'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix="LMbPt").first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        sample_id_provider = PseudoRandomIdProvider.query.filter_by(prefix="LMbSa").first()
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
