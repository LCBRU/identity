from identity.setup.studies import StudyName
from identity.model.id import (
    PseudoRandomIdProvider,
    StudyIdSpecification,
)
from .model import (
    PRINTER_TMF_SAMPLE,
    PRINTER_TMF_BAG,
    BagContext,
    SampleContext,
    LabelPack,
    LabelSet,
)
from .printing_methods import (
    print_barcode,
    print_notes_label,
)
from lbrc_flask.database import db


ID_TYPE_PARTICIPANT = "GDPt"
ID_TYPE_SAMPLE = "GDSa"


class GoDcmIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.GO_DCM,
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'GO-DCM Participants'},
                {ID_TYPE_SAMPLE: 'GO-DCM Samples'},
            ],
        )


class GoDcmPack(LabelPack):
    
    __mapper_args__ = {
        "polymorphic_identity": 'GoDcmPack',
    }

    __study_name__ = StudyName.GO_DCM

    def set_participant_id(self, participant_id):
        self._participant_id = participant_id

    def user_defined_participant_id(self):
        return True

    def allow_batch_printing(self):
        return False

    def _do_print(self):

        self.save_participant_id(self._participant_id)

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=self._participant_id,
            side_bar=self.__study_name__['name'],
        )

        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        substudy_sst_set = LabelSet(
            bag_context=bag_context,
            sample_context=sample_context,
            title='GO-DCM Substudy EDTA 2 Bag',
            version='1.1',
            on_ice=False,
        )
        substudy_sst_set.add_sample(name='EDTA', volume='2.7')
        substudy_sst_set.print()

        substudy_edta_set = LabelSet(
            bag_context=bag_context,
            sample_context=sample_context,
            title='GO-DCM Substudy EDTA Bag',
            version='1.0',
            on_ice=True,
        )
        substudy_edta_set.add_sample(name='EDTA', volume='7.9')
        substudy_edta_set.print()

        baseline_serum_set = LabelSet(
            bag_context=bag_context,
            sample_context=sample_context,
            title='GO-DCM Baseline Serum Bag',
            version='1.0',
            on_ice=False,
        )
        baseline_serum_set.add_sample(name='Serum', volume='4.9')
        baseline_serum_set.print()

        baseline_edta_set = LabelSet(
            bag_context=bag_context,
            sample_context=sample_context,
            title='GO-DCM Baseline EDTA Bag',
            version='1.0',
            on_ice=True,
        )
        baseline_edta_set.add_sample(name='EDTA', volume='10')
        baseline_edta_set.add_sample(name='Li Hep Plasma', volume='4.9')
        baseline_edta_set.print()

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=self._participant_id,
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
            participant_id=self._participant_id,
        )
