#!/usr/bin/env python3

from .alleviate import *
from .bioresource import *
from .brave import *
from .briccs import *
from .cae import *
from .cardiomet import *
from .cia import *
from .cmr_vs_ctffr import *
from .cosmic import *
from .discordance import *
from .elastic_as import *
from .fast import *
from .go_dcm import *
from .hic_covid import *
from .indapamide import *
from .lenten import *
from .limb import *
from .mermaid import *
from .predict import *
from .preeclampsia import *
from .scad import *
from .spiral import *


def init_printing(app):
    pass


class TestLabelPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'TestPack',
    }

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix="AllPt").first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        self.save_participant_id(participant_id)

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar='Test',
        )

        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix="AllSa").first(),
        )

        print_bag(
            label_context=bag_context,
            title='ALLEVIATE (room temp)',
            subset='Subset',
            version='v1.0',
            subheaders=[
                '1 x 4.9ml Serum (brown)',
                '1 x 2.7ml EDTA (purple)',
            ],
            warnings=['Transfer to lab within 90 minutes']
        )

        print_sample(
            label_context=sample_context,
            title='4.9ml Serum (brown)'
        )

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=participant_id,
            count=2,
        )

        pid2_provider = SequentialIdProvider.query.filter_by(prefix="ScadReg").first()
        pid2 = pid2_provider.allocate_id(current_user).barcode

        self.save_participant_id(pid2)

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=pid2,
        )

        pid3_provider = LegacyIdProvider.query.filter_by(prefix="BPt").first()
        pid3 = pid3_provider.allocate_id(current_user).barcode

        self.save_participant_id(pid3)

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=pid3,
        )

        pid4_provider = BioresourceIdProvider.query.filter_by(prefix="BR").first()
        pid4 = pid4_provider.allocate_id(current_user).barcode

        self.save_participant_id(pid4)

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=pid4,
        )

