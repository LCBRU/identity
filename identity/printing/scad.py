from flask_login import current_user
from ..model import (
    PseudoRandomIdProvider,
    SequentialIdProvider,
)
from .model import (
    print_sample,
    PRINTER_BRU_CRF_BAG,
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    BagContext,
    LabelPack,
    print_notes_label,
)
from .briccs import BriccsBags

ID_NAME_SCAD_REG = 'SCAD REG IDS'
PREFIX_SCAD_REG = 'ScadReg'


class ScadPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'ScadPack',
    }

    __study_name__ = 'SCAD'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix='ScPt').first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='SCAD',
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix='ScSa').first(),
        )

        bb = BriccsBags()
        bb.print_citrate_bag(bag_context=bag_context, sample_context=sample_context)
        bb.print_serum_bag(bag_context=bag_context, sample_context=sample_context)
        bb.print_urine_bag(bag_context=bag_context, sample_context=sample_context)

        print_notes_label(
            label_context=bag_context,
            study_a='Epidemiology, management, outcomes',
            study_b='and pathophysiology of SCAD',
            chief_investigator='Dave Adlam',
            chief_investigator_email='da134@le.ac.uk / dave.adlam@uhl-tr.nhs.uk',
            study_sponsor='University of Leicester',
            iras_id='18234',
            version='1.0',
            participant_id=participant_id,
        )
        
        print_sample(sample_context)


class ScadBloodOnlyPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'ScadBloodOnlyPack',
    }

    __study_name__ = 'SCAD'

    def print(self):
        print_sample(SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix='ScPt').first(),
        ))

        for _ in range(3):
            print_sample(SampleContext(
                printer=PRINTER_BRU_CRF_SAMPLE,
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix='ScSa').first(),
            ))


class ScadFamilyPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'ScadFamilyPack',
    }

    __study_name__ = 'SCAD'

    def print(self):
        print_sample(
            SampleContext(
                printer=PRINTER_BRU_CRF_SAMPLE,
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix='ScFm').first(),
            ),
            count=7,
        )


class ScadRegistryPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'ScadRegistryPack',
    }

    __study_name__ = 'SCAD'

    def print(self):
        print_sample(
            SampleContext(
                printer=PRINTER_BRU_CRF_SAMPLE,
                id_provider=SequentialIdProvider.query.filter_by(name=ID_NAME_SCAD_REG).first(),
            ),
            count=1,
        )
