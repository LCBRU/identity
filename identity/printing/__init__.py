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

import re
import socket
import datetime
import time
from flask import current_app
from flask_login import current_user


FONT_TINY = 'P'
FONT_SMALL = 'R'
FONT_MEDIUM = 'T'
FONT_LARGE = 'U'
FONT_TITLE = 'V'

_POS_BAG_LEFT_COL = 100
_POS_TITLE_TOP = 100
_POS_CONTENT_TOP = _POS_TITLE_TOP + 100

_WIDTH_BAG = 1200
_HEIGHT_BAG = 1500
_WIDTH_SAMPLE = 600
_LINE_HEIGHT = 55
_TITLE_LINE_HEIGHT = 80

_CODE_START = '^XA'
_CODE_WIDTH = '^PW{width}'
_CODE_NEXT_TEXT_CENTRED = '^FB{width},,,C'
_CODE_TEXT = '^FO{x},{y}^A{font}^FD{text}^FS'
_CODE_BARCODE = '^BY{width},3,{height}^FT{x},{y}^BCN,,Y,N^FD{barcode}^FS'
_CODE_BARCODE_LARGE_TEXT = '^BY{width},3,{height}^FT{x},{y}^AU^BCN,,Y,N^FD{barcode}^FS'
_CODE_BARCODE_ROTATED = '^BY{width},2.5,{height}^FT{x},{y}^AU^BCR,,Y,N^FD{barcode}^FS'
_CODE_QUANTITY = '^PQ{quantity},0,1,Y'
_CODE_LINE = '^FO{x},{y}^GB{width},0,5^FS'
_CODE_SIDE_BAR = '^FO1100,0^AVR^FD{side_bar}^FS'
_CODE_BAG_FORM = '''
^FO100,900^GB501,201,2^FS
^FB500,,,C
^FO100,910^A{font}^FD{str_date}^FS
^FO600,900^GB501,201,2^FS
^FB500,,,C
^FO600,910^A{font}^FD{str_time_sample_taken}^FS
^FO100,1100^GB501,201,2^FS
^FB500,,,C
^FO100,1110^A{font}^FD{str_emergency_consent}^FS
^FO600,1100^GB501,201,2^FS
^FB500,,,C
^FO600,1110^A{font}^FD{str_full_consent}^FS
^FB500,,,C
^FO600,1150^A{font}^FD{str_full_consent_b}^FS
'''
_CODE_NOTES_FORM = '''
^FO100,700^GB501,201,2^FS
^FB500,,,C
^FO100,710^A{font}^FDVersion and date of PIS^FS
^FO600,700^GB501,201,2^FS
^FB500,,,C
^FO600,710^A{font}^FDIncomplete CF returned^FS
^FB500,,,C
^FO600,750^A{font}^FDto participant?^FS
^FB500,,,C
^FO600,830^A{font}^FDY / N / Not Applicable^FS
^FO100,900^GB501,201,2^FS
^FB500,,,C
^FO100,910^A{font}^FDDate fully completed^FS
^FB500,,,C
^FO100,950^A{font}^FDconsent received^FS
^FO600,900^GB501,201,2^FS
^FB500,,,C
^FO600,910^A{font}^FDCopies of PIS and CF^FS
^FB500,,,C
^FO600,950^A{font}^FDplaced in notes?^FS
^FB500,,,C
^FO600,1030^A{font}^FDY / N^FS
^FO100,1100^GB501,201,2^FS
^FB500,,,C
^FO100,1110^A{font}^FDParticipant meets^FS
^FB500,,,C
^FO100,1150^A{font}^FDinclusion criteria?^FS
^FB500,,,C
^FO100,1230^A{font}^FDY / N^FS
^FO600,1100^GB501,201,2^FS
^FB500,,,C
^FO600,1110^A{font}^FDParticipant added to^FS
^FB500,,,C
^FO600,1150^A{font}^FDenrolment log?^FS
^FB500,,,C
^FO600,1230^A{font}^FDY / N^FS
'''
_CODE_END = '^XZ'


class Label:
    WIDTH_BAG = _WIDTH_BAG
    WIDTH_SAMPLE = _WIDTH_SAMPLE
    HEIGHT_BAG = _HEIGHT_BAG

    def __init__(self, width, height=0, count=1):
        self.width = width
        self.height = height
        self.count = count
        self.instructions = []
    
    def get_code(self):
        code = []
        code.append(_CODE_START)
        code.append(_CODE_WIDTH.format(width=self.width))

        code.extend(self.instructions)

        code.append(_CODE_QUANTITY.format(quantity=self.count))
        code.append(_CODE_END)

        return ''.join(code)

    def add_text(self, text, x_pos, y_pos, font, centered=False):
        if centered:
            self.instructions.append(_CODE_NEXT_TEXT_CENTRED.format(width=self.width))

        self.instructions.append(_CODE_TEXT.format(
                x=x_pos,
                y=y_pos,
                font=font,
                text=text,
            ))

    def add_sidebar(self, text):
        self.instructions.append(_CODE_NEXT_TEXT_CENTRED.format(width=self.height))
        self.instructions.append(_CODE_SIDE_BAR.format(side_bar=text))

    def add_barcode(self, barcode, x_pos=0, y_pos=0, line_height=80, line_width=3, centered=False, rotated=False):
        if centered:
            x_pos = self._bar_code_centred_x(id=barcode, label_width=self.width)

        if rotated:
            code = _CODE_BARCODE_ROTATED
        else:
            code = _CODE_BARCODE

        self.instructions.append(code.format(
                width=line_width,
                x=x_pos,
                y=y_pos,
                height=line_height,
                barcode=self._encode_barcode(barcode),
            ))

    def add_barcode_large_text(self, barcode, x_pos=0, y_pos=0, line_height=80, line_width=3, centered=False):
        if centered:
            x_pos = self._bar_code_centred_x(id=barcode, label_width=self.width)

        self.instructions.append(_CODE_BARCODE_LARGE_TEXT.format(
                width=line_width,
                x=x_pos,
                y=y_pos,
                height=line_height,
                barcode=self._encode_barcode(barcode),
            ))

    def add_bag_form(
        self,
        font,
        str_date='Date',
        str_time_sample_taken='Time Sample Taken',
        str_emergency_consent='Emergency Consent',
        str_full_consent='Full Consent',
        str_full_consent_b=''
    ):
        self.instructions.append(
            _CODE_BAG_FORM.format(
                str_date=str_date,
                str_time_sample_taken=str_time_sample_taken,
                str_emergency_consent=str_emergency_consent,
                str_full_consent=str_full_consent,
                str_full_consent_b=str_full_consent_b,
                font=font,
            )
        )
    
    def _bar_code_centred_x(self, id, label_width):
        bar_code_width = (len(id) * 16) + 120
        return (label_width - bar_code_width) // 2

    def _encode_barcode(self, barcode):
        encoded_parts = []

        encoded_parts.append('>:')

        for p in re.split(r'(\d+)', barcode):
            if p.isnumeric():
                if len(p) % 2 == 1:
                    encoded_parts.append('>5')
                    encoded_parts.append(p[:-1])
                    encoded_parts.append('>6')
                    encoded_parts.append(p[-1:])
                else:
                    encoded_parts.append('>5')
                    encoded_parts.append(p)
                    encoded_parts.append('>6')
            else:
                encoded_parts.append(p)

        return ''.join(encoded_parts)


class LabelPrinter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hostname_or_ip_address = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.name

    def print_label(self, host, printer_code, port=9100):
        if current_app.config['TESTING']:
            #current_app.logger.info(f'Fake print of {printer_code} to host {host}')
            current_app.logger.info(f'.')
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((current_app.config[host], port))
                s.sendall(printer_code.encode('ascii'))
            time.sleep(0.1)


    def print_barcode(self, printer, barcode, count=1, title=''):
        label = Label(Label.WIDTH_SAMPLE, Label.HEIGHT_BAG, count=count)
        label.add_text(title, 50, 60, FONT_SMALL)
        label.add_barcode_large_text(barcode=barcode, x_pos=50)

        self.print_label(
            host=printer,
            printer_code=label.get_code(),
        )


    def print_sample(self, label_context, count=1, title=''):
        print_barcode(
            printer=label_context.sample_printer,
            barcode=label_context.sample_id_provider.allocate_id(current_user).barcode,
            count=count,
            title=title,
        )


    def print_recruited_notice(self, printer, study_name, count=1):
        label = Label(Label.WIDTH_SAMPLE, Label.HEIGHT_BAG, count=count)
        label.add_text('Patient recruited to research study:', 20, 30, FONT_MEDIUM)
        label.add_text(study_name, 20, 90, FONT_TITLE)
        label.add_text('Date Approached:', 20, 180, FONT_MEDIUM)
        label.add_text('Date Consented:', 20, 240, FONT_MEDIUM)

        self.print_label(
            host=printer,
            printer_code=label.get_code(),
        )


    def print_aliquot(self, printer, barcode, count=1):
        label = Label(Label.WIDTH_SAMPLE, Label.HEIGHT_BAG, count=count)
        label.add_barcode(barcode=barcode, x_pos=100, y_pos=30, line_width=2, rotated=True)
        label.add_barcode(barcode=barcode, x_pos=280, y_pos=30, line_width=2, rotated=True)
        label.add_barcode(barcode=barcode, x_pos=460, y_pos=30, line_width=2, rotated=True)

        self.print_label(
            host=printer,
            printer_code=label.get_code(),
        )


    def print_bag(
        self,
        label_context,
        title,
        version,
        subheaders=[],
        lines=[],
        warnings=[],
        subset='',
        count=1,
        str_date='Date',
        str_time_sample_taken='Time Sample Taken',
        str_emergency_consent='Emergency Consent',
        str_full_consent='Full Consent',
        str_full_consent_b='',
    ):
        label = Label(Label.WIDTH_BAG, Label.HEIGHT_BAG, count=count)
        label.add_text(title, 0, _POS_TITLE_TOP, label_context.FONT_TITLE, centered=True)
        label.add_sidebar(text=label_context.side_bar + ' ' + subset)

        y = _POS_CONTENT_TOP

        for sh in subheaders:
            label.add_text(text=sh, x_pos=0, y_pos=y, font=label_context.FONT_LARGE, centered=True)
            y += _LINE_HEIGHT

        if subheaders:
            y += _LINE_HEIGHT

        for l in lines:
            label.add_text(text=l, x_pos=_POS_BAG_LEFT_COL, y_pos=y, font=label_context.FONT_MEDIUM)
            y += _LINE_HEIGHT

        if lines:
            y += _LINE_HEIGHT

        for w in warnings:
            y += _LINE_HEIGHT
            label.add_text(text=w, x_pos=0, y_pos=y, font=label_context.FONT_LARGE, centered=True)
            y += _LINE_HEIGHT

        label.add_bag_form(
            font=label_context.FONT_MEDIUM,
            str_date=str_date,
            str_time_sample_taken=str_time_sample_taken,
            str_emergency_consent=str_emergency_consent,
            str_full_consent=str_full_consent,
            str_full_consent_b=str_full_consent_b,
        )

        label.add_barcode(barcode=label_context.participant_id, y_pos=1400, centered=True)
        label.add_text(
            text='{version} printed {date}'.format(
                    version=version,
                    date=datetime.date.today().strftime("%d %B %Y"),
                ),
            x_pos=0,
            y_pos=1475,
            font=label_context.FONT_SMALL,
            centered=True,
        )

        self.print_label(
            host=label_context.bag_printer,
            printer_code=label.get_code(),
        )


    def print_bag_small(
        self,
        printer,
        title,
        line_1,
        line_2,
        count=1,
    ):
        code = [
            _CODE_START,
            _CODE_TEXT.format(
                x=0,
                y=30,
                font=FONT_TITLE,
                text=title,
            ),
            _CODE_TEXT.format(
                x=0,
                y=120,
                font=FONT_MEDIUM,
                text=line_1,
            ),
            _CODE_TEXT.format(
                x=0,
                y=180,
                font=FONT_MEDIUM,
                text=line_2,
            ),
            _CODE_TEXT.format(
                x=0,
                y=240,
                font=FONT_MEDIUM,
                text='Please affix participant ID label',
            ),
            _CODE_QUANTITY.format(quantity=count),
            _CODE_END,
        ]

        self.print_label(
            host=printer,
            printer_code=''.join(code),
        )


    def print_notes_label(
        self,
        label_context,
        study_a,
        chief_investigator,
        chief_investigator_email,
        study_sponsor,
        iras_id,
        version,
        participant_id,
        study_b='',
    ):
        y = _POS_TITLE_TOP

        code = [
            _CODE_START,
            _CODE_WIDTH.format(width=_WIDTH_BAG),
            _CODE_NEXT_TEXT_CENTRED.format(width=_WIDTH_BAG),
            _CODE_TEXT.format(
                x=0,
                y=y,
                font=label_context.FONT_MEDIUM,
                text='Participant in the following research study:',
            ),
        ]
        y += _TITLE_LINE_HEIGHT

        code.extend([
            _CODE_NEXT_TEXT_CENTRED.format(width=_WIDTH_BAG),
            _CODE_TEXT.format(
                x=0,
                y=y,
                font=label_context.FONT_TITLE,
                text=study_a,
            ),
        ])
        y += _TITLE_LINE_HEIGHT

        code.extend([
            _CODE_NEXT_TEXT_CENTRED.format(width=_WIDTH_BAG),
            _CODE_TEXT.format(
                x=0,
                y=y,
                font=label_context.FONT_TITLE,
                text=study_b,
            ),
        ])
        y += _TITLE_LINE_HEIGHT
        y += _TITLE_LINE_HEIGHT

        code.extend([
            _CODE_TEXT.format(
                x=_POS_BAG_LEFT_COL,
                y=y,
                font=label_context.FONT_MEDIUM,
                text='Participant ID:' + participant_id,
            ),
        ])
        y += _LINE_HEIGHT

        code.extend([
            _CODE_TEXT.format(
                x=_POS_BAG_LEFT_COL,
                y=y,
                font=label_context.FONT_MEDIUM,
                text='Chief Investigator:' + chief_investigator,
            ),
        ])
        y += _LINE_HEIGHT

        code.extend([
            _CODE_TEXT.format(
                x=_POS_BAG_LEFT_COL,
                y=y,
                font=label_context.FONT_MEDIUM,
                text='Chief Email:' + chief_investigator_email,
            ),
        ])
        y += _LINE_HEIGHT

        code.extend([
            _CODE_TEXT.format(
                x=_POS_BAG_LEFT_COL,
                y=y,
                font=label_context.FONT_MEDIUM,
                text='Study Sponsor:' + study_sponsor,
            ),
        ])
        y += _LINE_HEIGHT

        code.extend([
            _CODE_TEXT.format(
                x=_POS_BAG_LEFT_COL,
                y=y,
                font=label_context.FONT_MEDIUM,
                text='IRAS ID:' + iras_id,
            ),
        ])
        y += _LINE_HEIGHT

        code.extend([
            _CODE_NOTES_FORM.format(
                font=label_context.FONT_MEDIUM,
            ),
            _CODE_NEXT_TEXT_CENTRED.format(width=_WIDTH_BAG),
            _CODE_TEXT.format(
                x=0,
                y=1475,
                font=label_context.FONT_SMALL,
                text='{version} printed {date}'.format(
                    version=version,
                    date=datetime.date.today().strftime("%d %B %Y"),
                ),
            ),
            _CODE_QUANTITY.format(quantity=1),
            _CODE_END,
        ])

        self.print_label(
            host=label_context.bag_printer,
            printer_code=''.join(code),
        )

class LabelPrinterSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bag_printer_id = db.Column(db.Integer, db.ForeignKey(LabelPrinter.id))
    bag_printer = db.relationship(LabelPrinter, foreign_keys=[bag_printer_id])
    sample_printer_id = db.Column(db.Integer, db.ForeignKey(LabelPrinter.id))
    sample_printer = db.relationship(LabelPrinter, foreign_keys=[sample_printer_id])

    def __repr__(self):
        return self.name


class LabelBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id))
    study = db.relationship(Study, backref=db.backref("label_batches"))
    participant_id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    participant_id_provider = db.relationship(IdProvider, foreign_keys=[participant_id_provider_id])
    sample_id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    sample_id_provider = db.relationship(IdProvider, foreign_keys=[sample_id_provider_id])
    aliquot_id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    aliquot_id_provider = db.relationship(IdProvider, foreign_keys=[aliquot_id_provider_id])
    label_printer_set_id = db.Column(db.Integer, db.ForeignKey(LabelPrinterSet.id))
    label_printer_set = db.relationship(LabelPrinterSet)
    disable_batch_printing = db.Column(db.Boolean)
    print_recruited_notice = db.Column(db.Boolean)

    def __repr__(self):
        return f'{self.study.name}: {self.name}'

    def print(self, count):
        for _ in range(count):
            self.print_batch()
        
        if self.print_recruited_notice:
            self.label_printer_set.sample_printer.print_recruited_notice(printer=PRINTER_TMF_SAMPLE, study_name=self.study.name)

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

        for bs in self.bags:
            bs.print(participant_id, self)


class SampleBagLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_num = db.Column(db.Integer, nullable=False)
    label_batch_id = db.Column(db.Integer, db.ForeignKey(LabelBatch.id))
    label_batch = db.relationship(LabelBatch, backref=db.backref("bags"))
    title = db.Column(db.String(100), nullable=False)
    visit = db.Column(db.String(100), nullable=False)
    subheaders = db.Column(db.Text, nullable=False)
    warnings = db.Column(db.Text, nullable=False)

    __mapper_args__ = {
        "version_id_col": version_num,
    }

    def print(self, participant_id, context):

        bag_context = BagContext(
            printer=PRINTER_TMF_BAG,
            participant_id=participant_id,
            side_bar=self.label_batch.study.name,
        )

        context.label_printer_set.bag_printer.print_bag(
            label_context=bag_context,
            title=self.title,
            subset=self.visit,
            version=f'v{self.version_num}',
            subheaders=self.subheaders.splitlines(),
            warnings=self.warnings.splitlines()
        )

        for s in self.samples:
            s.print(context)
        
        if len(self.aliquots) > 0:
            aliquot_id = context.aliquot_id_provider.allocate_id(current_user).id

            for a in self.aliquots:
                a.print(aliquot_id, context)


class SampleLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_bag_label_id = db.Column(db.Integer, db.ForeignKey(SampleBagLabel.id))
    sample_bag_label = db.relationship(SampleBagLabel, backref=db.backref("samples"))
    name = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False, default=1)

    def print(self, context):
        sample_context = SampleContext(
            printer=PRINTER_TMF_SAMPLE,
            id_provider=context.sample_id_provider,
        )

        for _ in range(self.count):
            context.label_printer_set.sample_printer.print_sample(
                label_context=sample_context,
                title=self.name
            )


class AliquotLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_bag_label_id = db.Column(db.Integer, db.ForeignKey(SampleBagLabel.id))
    sample_bag_label = db.relationship(SampleBagLabel, backref=db.backref("aliquots"))
    prefix = db.Column(db.String(10), nullable=False)
    count = db.Column(db.Integer, nullable=False, default=1)

    def print(self, aliquot_id, context):
        if self.count > 1:
            for i in range(1, self.count + 1):
                context.label_printer_set.sample_printer.print_aliquot(
                    printer=PRINTER_TMF_SAMPLE,
                    barcode=f'{self.prefix}{aliquot_id}-{i}',
                )
        else:
            context.label_printer_set.sample_printer.print_aliquot(
                printer=PRINTER_TMF_SAMPLE,
                barcode=f'{self.prefix}{aliquot_id}',
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

        print_recruited_notice(
            printer=PRINTER_TMF_SAMPLE,
            study_name='ELASTIC-AS',
        )
