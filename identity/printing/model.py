import re
import time
from collections import namedtuple
from flask import current_app
from flask_login import current_user
from ..database import db
from identity.model.id import (
    Study,
    ParticipantIdentifier,
    ParticipantIdentifierType,
)
from .printing_methods import (
    FONT_TINY,
    FONT_SMALL,
    FONT_MEDIUM,
    FONT_LARGE,
    FONT_TITLE,
    print_sample,
    print_bag,
)



PRINTER_CVRC_LAB_SAMPLE = 'PRINTER_CVRC_LAB_SAMPLE'
PRINTER_BRU_CRF_SAMPLE = 'PRINTER_BRU_CRF_SAMPLE'
PRINTER_BRU_CRF_BAG = 'PRINTER_BRU_CRF_BAG'
PRINTER_LIMB = 'PRINTER_LIMB'
PRINTER_TMF_SAMPLE = 'PRINTER_TMF_SAMPLE'
PRINTER_TMF_BAG = 'PRINTER_TMF_BAG'
PRINTER_ADDRESS = 'PRINTER_ADDRESS'


class BagContext():
    def __init__(self, printer, participant_id, side_bar, small_fonts=False):
        self.bag_printer = printer
        self.participant_id = participant_id
        self.side_bar = side_bar
        
        if small_fonts:
            self.FONT_SMALL = FONT_SMALL
            self.FONT_MEDIUM = FONT_SMALL
            self.FONT_LARGE = FONT_MEDIUM
            self.FONT_TITLE = FONT_LARGE
        else:
            self.FONT_SMALL = FONT_SMALL
            self.FONT_MEDIUM = FONT_MEDIUM
            self.FONT_LARGE = FONT_LARGE
            self.FONT_TITLE = FONT_TITLE


class SampleContext():
    def __init__(self, printer, id_provider):
        self.sample_printer = printer
        self.sample_id_provider = id_provider


class LabelPack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id))
    study = db.relationship(Study, backref=db.backref("label_packs"))

    __mapper_args__ = {
        "polymorphic_identity": "Pack",
        "polymorphic_on": type,
    }

    def user_defined_participant_id(self):
        return False

    def allow_batch_printing(self):
        return True

    @property
    def name(self):
        return re.sub('([a-z])([A-Z])', r'\1 \2', self.__class__.__name__)

    def print(self, count):
        for _ in range(count):
            current_app.logger.info(f'Printing label for study {self.study.name}')

            self._do_print()

            db.session.commit()

            time.sleep(current_app.config['PRINTING_SET_SLEEP'])

    def save_participant_id(self, participant_id):
        pit = ParticipantIdentifierType.get_study_participant_id()

        pi = ParticipantIdentifier.query.filter_by(
            participant_identifier_type_id=pit.id,
            identifier=participant_id,
        ).one_or_none()

        if pi is None:
            db.session.add(ParticipantIdentifier(
                participant_identifier_type_id=pit.id,
                identifier=participant_id,
                last_updated_by_user_id=current_user.id,
            ))


    def _do_print(self, participant_id=None):
        pass

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name


class LabelSet():

    Sample = namedtuple('Sample', ['name', 'volume', 'count'])

    def __init__(
        self,
        bag_context,
        sample_context,
        title,
        version,
        on_ice=False,
    ):
        self.bag_context = bag_context
        self.sample_context = sample_context
        self.title = title
        self.version = version
        self.on_ice = on_ice
        self.samples = []
        self.lines = []
        self.warnings = []

    def add_sample(self, name, volume, count=1):
        self.samples.append(
            self.Sample(name=name, volume=volume, count=count)
        )

    def add_line(self, line):
        self.lines.append(line)

    def add_warning(self, line):
        self.warnings.append(line)

    def print(self):
        lines = self.lines

        if self.on_ice:
            lines.extend([
                'Put on ice for 2 minutes',
                'Return to bag then put back on ice',           
            ])
        else:
            lines.append('DO NOT PUT ON ICE')

        warnings = self.warnings
        warnings.append('Transfer to lab within 90 minutes')

        print_bag(
            label_context=self.bag_context,
            title=self.title,
            version=f'v{self.version}',
            subheaders=[f'{s.count} x {s.volume}ml {s.name}' for s in self.samples],
            lines=[f'* {l}' for l in lines],
            warnings=warnings,
        )
        for s in self.samples:
            print_sample(self.sample_context, s.count, title=f'{s.volume}ml {s.name}')
