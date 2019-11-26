from flask_login import current_user
from ..model import PseudoRandomIdProvider
from .model import (
    print_bag,
    print_sample,
    print_recruited_notice,
    PRINTER_BRU_CRF_SAMPLE,
    PRINTER_BRU_CRF_BAG,
    BagContext,
    SampleContext,
    LabelPack,
    print_notes_label,
)


class CaePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'CaePack',
    }

    __study_name__ = 'CAE'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix="CaePt").first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='CAE',
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix="CaeSa").first(),
        )

        print_bag(
            label_context=bag_context,
            title='Serum and EDTA Bag',
            version='v3.0',
            subheaders=[
                '1 x 7.5ml Serum',
                '1 x 7.5ml EDTA',
                '1 x 2.7ml EDTA',
            ],
            lines=[
                '* Fill brown 7.5ml serum bottle 1st',
                '* KEEP AT ROOM TEMPERATURE',
                '* Fill red 7.5ml EDTA bottle 2nd',
                '* PUT ON ICE',
                '* Fill purple 2.7ml EDTA bottle 3rd',
                '* KEEP AT ROOM TEMPERATURE',
            ],
            warnings=[
                'Transfer to lab within 90 minutes',
            ],
        )
        print_sample(
            label_context=sample_context,
            title='2.7ml EDTA'
        )
        print_sample(
            label_context=sample_context,
            title='7.5ml EDTA'
        )
        print_sample(
            label_context=sample_context,
            title='7.5ml Serum'
        )

        print_notes_label(
            label_context=bag_context,
            study_a='Causes of Acute Coronary Syndrome',
            study_b='in People with SCAD or CAE',
            chief_investigator='Dave Adlam',
            chief_investigator_email='da134@le.ac.uk / dave.adlam@uhl-tr.nhs.uk',
            study_sponsor='University of Leicester',
            iras_id='182079',
            version='1.0',
            participant_id=participant_id,
        )
