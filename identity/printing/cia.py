from flask_login import current_user
from ..model import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    print_bag,
    print_barcode,
    print_sample,
    PRINTER_BRU_CRF_SAMPLE,
    PRINTER_BRU_CRF_BAG,
    BagContext,
    SampleContext,
    LabelPack,
)


ID_TYPE_PARTICIPANT = "CiaPt"
ID_TYPE_SAMPLE = "CiaSa"


class CiaIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='CIA',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'CIA Participants'},
                {ID_TYPE_SAMPLE: 'CIA Samples'},
            ],
        )


class CiaPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'CiaPack',
    }

    __study_name__ = 'CIA'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='CIA',
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        print_bag(
            label_context=bag_context,
            title='CIA EDTA Bag',
            version='v3.0',
            subheaders=['1 x 9.8ml EDTA tube'],
        )
        print_sample(
            label_context=sample_context,
            title='9.8ml EDTA'
        )

        print_bag(
            label_context=bag_context,
            title='CIA Serum Bag',
            version='v3.0',
            subheaders=['1 x 9.8ml Serum tube'],
        )
        print_sample(
            label_context=sample_context,
            title='9.8ml Serum'
        )

        print_barcode(
            printer=PRINTER_BRU_CRF_SAMPLE,
            barcode=participant_id,
            count=5,
        )
