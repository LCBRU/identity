from identity.setup.studies import StudyName
from flask_login import current_user
from identity.model.id import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    PRINTER_TMF_BAG,
    PRINTER_TMF_SAMPLE,
    SampleContext,
    BagContext,
    LabelPack,
)
from .printing_methods import (
    print_sample,
    print_bag,
    print_barcode,
)


ID_TYPE_PARTICIPANT = "AllPt"
ID_TYPE_SAMPLE = "AllSa"


class AlleviateIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.ALLEVIATE,
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'ALLEVIATE Participants'},
                {ID_TYPE_SAMPLE: 'ALLEVIATE Samples'},
            ],
        )


class AlleviatePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'AlleviatePack',
    }

    __study_name__ = StudyName.ALLEVIATE

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id().barcode

        self.save_participant_id(participant_id)

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar=StudyName.ALLEVIATE['name'],
        )

        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        for subset in ['Baseline', '12 Weeks']:
            print_bag(
                label_context=bag_context,
                title='ALLEVIATE (room temp)',
                subset=subset,
                version='v4.0',
                subheaders=[
                    '1 x 4.9ml Serum (brown)',
                    '1 x 2.7ml EDTA (purple)',
                ],
                warnings=['Transfer to lab within 90 minutes']
            )

            print_bag(
                label_context=bag_context,
                title='ALLEVIATE (on ice)',
                subset=subset,
                version='v4.0',
                subheaders=[
                    '2 x 4.9ml Litium Hep. (orange)',
                    '1 x 4.9ml EDTA (pink)',
                ],
                warnings=[
                    'Put on ice',
                    'Transfer to lab within 90 minutes'
                ]
            )
        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title='4.9ml Serum (brown)'
            )
        for _ in range(4):
            print_sample(
                label_context=sample_context,
                title='4.9ml Lithium Hep. (orange)'
            )

        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title='4.9ml EDTA (pink)'
            )

        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title='2.7ml EDTA (purple)'
            )

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=participant_id,
            count=35,
        )
