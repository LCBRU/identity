from identity.setup.studies import StudyName
from flask_login import current_user
from identity.model.id import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    BagContext, LabelSet, PRINTER_TMF_BAG,
    PRINTER_TMF_SAMPLE,
    LabelPack, SampleContext,
)
from .printing_methods import (
    print_notes_label, print_barcode,
)


ID_TYPE_PARTICIPANT = "CvCPt"
ID_TYPE_SAMPLE = "CvCSa"


class CmrVsCtffrIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.CMR_vs_CTFFR,
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'CMR vs CT-FFR Participants'},
                {ID_TYPE_SAMPLE: 'CMR vs CT-FFR Samples'},
            ],
        )


class CmrVsCtffrPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'CmrVsCtffrPack',
    }

    __study_name__ = StudyName.CMR_vs_CTFFR

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        self._participant_id = participant_id_provider.allocate_id().barcode

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

        substudy_edta_set = LabelSet(
            bag_context=bag_context,
            sample_context=sample_context,
            title='CMR vs CT-FFR EDTA Bag',
            version='1.0',
            on_ice=True,
        )
        substudy_edta_set.add_sample(name='EDTA (pink)', volume='4.9')
        substudy_edta_set.print()

        baseline_serum_set = LabelSet(
            bag_context=bag_context,
            sample_context=sample_context,
            title='CMR vs CT-FFR Serum Bag',
            version='1.0',
            on_ice=False,
        )
        baseline_serum_set.add_sample(name='Serum (brown)', volume='4.9')
        baseline_serum_set.print()

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=self._participant_id,
            count=4,
        )

        print_notes_label(
            label_context=bag_context,
            study_a='CMR vs CT-FFR in CAD',
            chief_investigator='Dr Jayanth R Arnold',
            chief_investigator_email='jra14@leicester.ac.uk',
            study_sponsor='University of Leicester',
            iras_id='258996',
            version='1.0',
            participant_id=self._participant_id,
        )
