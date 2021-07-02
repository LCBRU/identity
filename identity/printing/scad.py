from flask import current_app
from flask_login import current_user
from identity.model.id import (
    PseudoRandomIdProvider,
    SequentialIdProvider,
    StudyIdSpecification,
)
from .model import (
    PRINTER_BRU_CRF_BAG,
    PRINTER_BRU_CRF_SAMPLE,
    SampleContext,
    BagContext,
    LabelPack,
)
from .printing_methods import (
    print_barcode,
    print_notes_label,
)
from identity.setup.studies import StudyName
from .briccs import BriccsBags

ID_NAME_SCAD_REG = 'SCAD REG IDS'
PREFIX_SCAD_REG = 'ScadReg'


ID_TYPE_PARTICIPANT = "ScPt"
ID_TYPE_SAMPLE = "ScSa"
ID_TYPE_FAMILY = "ScFm"


class ScadIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.SCAD,
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'SCAD Participants'},
                {ID_TYPE_SAMPLE: 'SCAD Samples'},
                {ID_TYPE_FAMILY: 'SCAD Families'},
            ],
            sequential_identifier_types=[
                {
                    'prefix': PREFIX_SCAD_REG,
                    'name': ID_NAME_SCAD_REG,
                    'zero_fill_size': 5,
                    'last_number': 1999,
                },
            ],
        )


class ScadPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'ScadPack',
    }

    __study_name__ = StudyName.SCAD

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode
        sample_id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first()

        self.save_participant_id(participant_id)

        current_app.logger.error(f'Print for {participant_id}')

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='SCAD',
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=sample_id_provider,
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
        
        print_barcode(printer=PRINTER_BRU_CRF_SAMPLE, barcode=sample_id_provider.allocate_id(current_user).barcode)


class ScadBloodOnlyPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'ScadBloodOnlyPack',
    }

    __study_name__ = StudyName.SCAD

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode
        sample_id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first()

        self.save_participant_id(participant_id)

        print_barcode(
            printer=PRINTER_BRU_CRF_SAMPLE,
            barcode=participant_id,
        )

        for _ in range(3):
            print_barcode(
                printer=PRINTER_BRU_CRF_SAMPLE,
                barcode=sample_id_provider.allocate_id(current_user).barcode,
            )


class ScadFamilyPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'ScadFamilyPack',
    }

    __study_name__ = StudyName.SCAD

    def _do_print(self):
        family_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_FAMILY).first()
        family_id = family_id_provider.allocate_id(current_user).barcode

        print_barcode(
            printer=PRINTER_BRU_CRF_SAMPLE,
            barcode=family_id,
            count=7,
        )


class ScadRegistryPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'ScadRegistryPack',
    }

    __study_name__ = StudyName.SCAD

    def _do_print(self):
        registry_id_provider = SequentialIdProvider.query.filter_by(name=ID_NAME_SCAD_REG).first()
        registry_id = registry_id_provider.allocate_id(current_user).barcode

        print_barcode(
            printer=PRINTER_BRU_CRF_SAMPLE,
            barcode=registry_id,
            count=1,
        )
