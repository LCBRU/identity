from flask_login import current_user
from ..model import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    print_bag,
    print_barcode,
    print_sample,
    PRINTER_TMF_SAMPLE,
    PRINTER_TMF_BAG,
    BagContext,
    SampleContext,
    LabelPack,
    print_notes_label,
)


ID_TYPE_PARTICIPANT = "GDPt"
ID_TYPE_SAMPLE = "GDSa"


class GoDcmIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='GO-DCM',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'GO-DCM Participants'},
                {ID_TYPE_SAMPLE: 'GO-DCM Samples'},
            ],
        )


class GoDcmPack(LabelPack):
    
    __mapper_args__ = {
        "polymorphic_identity": 'GoDcmPack',
    }

    __study_name__ = 'GO-DCM'

    def set_participant_id(self, participant_id):
        self.participant_id = participant_id

    def user_defined_participant_id(self):
        return True

    def allow_batch_printing(self):
        return False

    def _do_print(self):
        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=self.participant_id,
            side_bar=self.__study_name__,
        )

        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        print_bag(
            label_context=bag_context,
            title='GO-DCM Substudy SST Bag',
            version='v1.0',
            subheaders=[
                '1 x 4.9ml SST',
            ],
            lines=[
                '* DO NOT PUT ON ICE',
            ],
            warnings=['Transfer to lab within 90 minutes'],
        )
        print_sample(
            label_context=sample_context,
            title='4.9ml SST'
        )

        print_bag(
            label_context=bag_context,
            title='GO-DCM Substudy EDTA Bag',
            version='v1.0',
            subheaders=[
                '1 x 7.9ml EDTA tube',
            ],
            lines=[
                '* Put on ice for 2 minutes',
                '* Return to bag then put back on ice',
            ],
            warnings=['Transfer to lab within 90 minutes'],
        )
        print_sample(
            label_context=sample_context,
            title='7.9ml EDTA'
        )

        print_bag(
            label_context=bag_context,
            title='GO-DCM Baseline Serum Bag',
            version='v1.0',
            subheaders=['1 x 4.9ml Serum tube'],
            warnings=[
                'DO NOT PUT ON ICE',
                'Transfer to lab within 90 minutes',
            ],
        )
        print_sample(
            label_context=sample_context,
            title='4.9ml Serum'
        )

        print_bag(
            label_context=bag_context,
            title='GO-DCM Baseline EDTA Bag',
            version='v1.0',
            subheaders=[
                '1 x 10ml EDTA tube',
                '1 x 4.9ml Li Hep Plasma tube',
            ],
            lines=[
                '* Put on ice for 2 minutes',
                '* Return to bag then put back on ice',
            ],
            warnings=['Transfer to lab within 90 minutes'],
        )
        print_sample(
            label_context=sample_context,
            title='4.9ml Li Hep'
        )
        print_sample(
            label_context=sample_context,
            title='10ml EDTA'
        )

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=self.participant_id,
            count=5,
        )

        print_notes_label(
            label_context=bag_context,
            study_a='Go DCM: Defining the genetics, biomarkers',
            study_b='and outcomes for dilated cardiomyopathy',
            chief_investigator='Dr James Ware',
            chief_investigator_email='j.ware@imperial.ac.uk',
            study_sponsor='NIHR CRN: North West London',
            iras_id='237880',
            version='1.0',
            participant_id=self.participant_id,
        )
