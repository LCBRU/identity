#!/usr/bin/env python3

from email.policy import default
from identity.model import Study
from identity.model.id import IdProvider, ParticipantIdentifier, ParticipantIdentifierType
from .alleviate import *
from .bioresource import *
from .brave import *
from .briccs import *
from .cae import *
from .cardiomet import *
from .cia import *
from .cmr_vs_ctffr import *
from .cosmic import *
from .discordance import *
from .elastic_as import *
from .fast import *
from .go_dcm import *
from .hic_covid import *
from .indapamide import *
from .lenten import *
from .limb import *
from .mermaid import *
from .predict import *
from .preeclampsia import *
from .scad import *
from .spiral import *


def init_printing(app):
    pass


class LabelBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id))
    study = db.relationship(Study, backref=db.backref("label_batches"))
    participant_id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    participant_id_provider = db.relationship(IdProvider, foreign_keys=[participant_id_provider_id])
    sample_id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    sample_id_provider = db.relationship(IdProvider, foreign_keys=[sample_id_provider_id])
    disable_batch_printing = db.Column(db.Boolean)

    def __repr__(self):
        return f'{self.study.name}: {self.name}'

    def print(self, count):
        for _ in range(count):
            self.print_batch()

    def _get_participant_id(self):
        result = self.participant_id_provider.allocate_id(current_user).barcode
    
        pit = ParticipantIdentifierType.get_study_participant_id()

        pi = ParticipantIdentifier.query.filter_by(
            participant_identifier_type_id=pit.id,
            identifier=result,
        ).one_or_none()

        if pi is None:
            db.session.add(ParticipantIdentifier(
                participant_identifier_type_id=pit.id,
                identifier=result,
                last_updated_by_user_id=current_user.id,
            ))

        return result


    def print_batch(self):
        participant_id = self._get_participant_id()

        for bs in self.sets:
            bs.print(participant_id)


class LabelBatchSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_num = db.Column(db.Integer, nullable=False)
    label_batch_id = db.Column(db.Integer, db.ForeignKey(LabelBatch.id))
    label_batch = db.relationship(LabelBatch, backref=db.backref("sets"))
    title = db.Column(db.String(100), nullable=False)
    visit = db.Column(db.String(100), nullable=False)
    subheaders = db.Column(db.Text, nullable=False)
    warnings = db.Column(db.Text, nullable=False)

    __mapper_args__ = {
        "version_id_col": version_num,
    }

    def print(self, participant_id):

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar=self.label_batch.study.name,
        )

        print_bag(
            label_context=bag_context,
            title=self.title,
            subset=self.visit,
            version=f'v{self.version_num}',
            subheaders=self.subheaders.splitlines(),
            warnings=self.warnings.splitlines()
        )


class SampleLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label_batch_set_id = db.Column(db.Integer, db.ForeignKey(LabelBatchSet.id))
    label_batch_set = db.relationship(LabelBatchSet, backref=db.backref("samples"))
    name = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False, default=1)

    def print(self):

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar=self.label_batch.study.name,
        )

        print_bag(
            label_context=bag_context,
            title=self.title,
            subset=self.visit,
            version=f'v{self.version_num}',
            subheaders=self.subheaders.splitlines(),
            warnings=self.warnings.splitlines()
        )


class TestLabelPack(LabelPack):
    __mapper_args__ = {
        "polymorphic_identity": 'TestPack',
    }

    def _do_print(self):
        participant_id_provider = PseudoRandomIdProvider.query.filter_by(prefix="AllPt").first()
        participant_id = participant_id_provider.allocate_id(current_user).barcode

        self.save_participant_id(participant_id)

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar='Test',
        )

        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=PseudoRandomIdProvider.query.filter_by(prefix="AllSa").first(),
        )

        print_bag(
            label_context=bag_context,
            title='ALLEVIATE (room temp)',
            subset='Subset',
            version='v1.0',
            subheaders=[
                '1 x 4.9ml Serum (brown)',
                '1 x 2.7ml EDTA (purple)',
            ],
            warnings=['Transfer to lab within 90 minutes']
        )

        print_sample(
            label_context=sample_context,
            title='4.9ml Serum (brown)'
        )

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=participant_id,
            count=2,
        )

        pid2_provider = SequentialIdProvider.query.filter_by(prefix="ScadReg").first()
        pid2 = pid2_provider.allocate_id(current_user).barcode

        self.save_participant_id(pid2)

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=pid2,
        )

        pid3_provider = LegacyIdProvider.query.filter_by(prefix="BPt").first()
        pid3 = pid3_provider.allocate_id(current_user).barcode

        self.save_participant_id(pid3)

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=pid3,
        )

        pid4_provider = BioresourceIdProvider.query.filter_by(prefix="BR").first()
        pid4 = pid4_provider.allocate_id(current_user).barcode

        self.save_participant_id(pid4)

        print_barcode(
            printer=PRINTER_TMF_SAMPLE,
            barcode=pid4,
        )

