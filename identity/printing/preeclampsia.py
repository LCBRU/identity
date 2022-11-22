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
)


ID_TYPE_PARTICIPANT = "PePt"
ID_TYPE_SAMPLE = "PeSa"


class PreelampsiaIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name=StudyName.Pre_Eclampsia,
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'PRE-ECLAMPSIA Participants'},
                {ID_TYPE_SAMPLE: 'PRE-ECLAMPSIA Samples'},
            ],
        )


class PreeclampsiaPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'PreeclampsiaPack',
    }

    __study_name__ = StudyName.Pre_Eclampsia

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id().barcode

        self.save_participant_id(participant_id)

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar='PRE-ECLAMPSIA',
        )

        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        print_bag(
            label_context=bag_context,
            title='EDTA Bag',
            version='v3.0',
            subheaders=[
                '3 x 7.5ml EDTA'
            ],
            lines=[
                'Fill EDTA bottles 2nd, 3rd AND 4th',
                'EDTA on ice for 2 minutes',
                'Return to bag then back on ice',
            ],
            warnings=['Transfer to lab within 90 minutes']
        )
        for _ in range(3):
            print_sample(
                label_context=sample_context,
                title='7.5ml EDTA'
            )

        print_bag(
            label_context=bag_context,
            title='Serum & EDTA Bag',
            version='v3.0',
            subheaders=[
                '1 x 7.5ml Serum',
                '1 x 2.7ml EDTA'
            ],
            lines=[
                'FILL Serum bottles 2nd, 3rd AND 4th',
                'EDTA on iCE for 2 minutes',
                'Return to bag then back on ice',
            ],
            warnings=['Transfer to lab within 90 minutes']
        )
        print_sample(
            label_context=sample_context,
            title='7.5ml Serum'
        )
        print_sample(
            label_context=sample_context,
            title='2.7ml EDTA'
        )
