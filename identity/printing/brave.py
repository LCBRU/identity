from flask_login import current_user
from ..model import PseudoRandomIdProvider, StudyIdSpecification
from .model import (
    print_bag,
    print_sample,
    PRINTER_BRU_CRF_SAMPLE,
    PRINTER_BRU_CRF_BAG,
    BagContext,
    SampleContext,
    LabelPack,
)
from .briccs import BriccsBags


ID_TYPE_PARTICIPANT = "BavPt"
ID_TYPE_SAMPLE = "BavSa"
ID_TYPE_FAMILY = "BavFm"
ID_TYPE_POLAND_PARTICIPANT = "BavPl"
ID_TYPE_EXTERNAL_PARTICIPANT = "BavXPt"


class AlleviateIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='BRAVE',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'BRAVE Participants'},
                {ID_TYPE_SAMPLE: 'BRAVE Samples'},
                {ID_TYPE_FAMILY: 'BRAVE Families'},
                {ID_TYPE_POLAND_PARTICIPANT: 'BRAVE Poland Participants'},
                {ID_TYPE_EXTERNAL_PARTICIPANT: 'BRAVE External Participants'},
            ],
        )


class BravePack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'BravePack',
    }

    __study_name__ = 'BRAVE'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='BAV',
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        bb = BriccsBags()
        bb.print_citrate_bag(bag_context=bag_context, sample_context=sample_context)
        bb.print_serum_bag(bag_context=bag_context, sample_context=sample_context)

        print_sample(
            label_context=SampleContext(
                printer=PRINTER_BRU_CRF_SAMPLE,
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_FAMILY).first(),
            ),
            count=7,
        )


class BraveExternalPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'BraveExternalPack',
    }

    __study_name__ = 'BRAVE'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_EXTERNAL_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='BAV External',
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        bb = BriccsBags()
        bb.print_edta_bag(bag_context=bag_context, sample_context=sample_context)

        print_sample(
            label_context=SampleContext(
                printer=PRINTER_BRU_CRF_SAMPLE,
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_FAMILY).first(),
            ),
            count=1,
        )


class BravePolandPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'BravePolandPack',
    }

    __study_name__ = 'BRAVE'

    def print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_POLAND_PARTICIPANT).first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        bag_context = BagContext(
            printer=PRINTER_BRU_CRF_BAG,
            participant_id=participant_id,
            side_bar='BAV Poland',
            small_fonts=True,
        )

        sample_context = SampleContext(
            printer=PRINTER_BRU_CRF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_SAMPLE).first(),
        )

        self.print_citrate_bag(bag_context, sample_context)
        self.print_serum_bag(bag_context, sample_context)

        print_sample(
            label_context=SampleContext(
                printer=PRINTER_BRU_CRF_SAMPLE,
                id_provider=PseudoRandomIdProvider.query.filter_by(prefix=ID_TYPE_FAMILY).first(),
            ),
            count=7,
        )

    def print_serum_bag(self, bag_context, sample_context):
        print_bag(
            label_context=bag_context,
            title='TOREBKA Z SUROWICA I PROBKA EDTA',
            version='v3.0',
            subheaders=[
                '1x7.5ml PROBKA NA SUROWICE (BRAZOWA)',
                '1x2.7ml PROBKA EDTA (FIOLETOWA)',
            ],
            lines=[
                '* POBIERZ PROBKE NA SUROWICE (PIERWSZA W KOLEJNOSCI)',
                '* UMIESC W TOREBCE',
                '* POBNIERZ PROBKE NA EDTA (PIATA W KOLEJNOSCIE)',
                '* UMIESC W TOREBCE',
                '* NIE UMIESZCZAJ NA LODZIE (TRZYMAJ W TEMPERATURZE POKOJOWEJ)',
            ],
            warnings=['DOSTARCZ DO LABORATORIUM W PRZECIAGU 90 MINUT'],
            str_date='DATA',
            str_time_sample_taken='GODZINA POBRANIA',
            str_emergency_consent='PROBKI',
            str_full_consent='OSOBA UZYSKUJA ZGODE',
            str_full_consent_b='NA UDZIAL W BADANIU',
        )
        print_sample(
            label_context=sample_context,
            title='7.5ml PROBKA NA SUROWICE (BRAZOWA)',
        )
        print_sample(
            label_context=sample_context,
            title='2.7ml PROBKA EDTA (FIOLETOWA)',
        )


    def print_citrate_bag(self, bag_context, sample_context):
        print_bag(
            label_context=bag_context,
            title='TOREBKA Z PROBKAMI EDTA I CYTRYNIANEM',
            version='v3.0',
            subheaders=[
                '1x4.3ml PROBKA NA KRZEPNIECIE Z CYTRYNIANEM (ZIELONA)',
                '2x7.5ml PROBKA EDTA (CZEROWNA)',
            ],
            lines=[
                '* UMIESC WSZYSTKIE 3 PROBKI NA LODZIE NA 2 MINUTY (ZEBY SCHLODZIC)',
                '* POBIERZ ZIELONA PROBKE NA KRZEPNIEZIE (DRUGA W KOLEJNOSCI)',
                '* POBIERZ 2 PROBKI NA EDTA (CZERWONE, TRZECIA I CZWARTA W KOLEJNOSCI)',
                '* UMIESC W TOREBCE I UMIESC NA LODZIE',
                '* TRYMAJ NA LODZIE',
            ],
            warnings=['DOSTARCZ DO LABORATORIUM W PRZECIAGU 90 MINUT'],
            str_date='DATA',
            str_time_sample_taken='GODZINA POBRANIA',
            str_emergency_consent='PROBKI',
            str_full_consent='OSOBA UZYSKUJA ZGODE',
            str_full_consent_b='NA UDZIAL W BADANIU',
        )
        print_sample(
            label_context=sample_context,
            title='4.3ml PROBKA NA KRZEPNIECIE Z CYTRYNIANEM (ZIELONA)',
        )
        for _ in range(2):
            print_sample(
                label_context=sample_context,
                title='7.5ml PROBKA EDTA (CZEROWNA)',
            )
