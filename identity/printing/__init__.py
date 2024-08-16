from identity.model import Study
from identity.model.id import IdProvider
from itertools import zip_longest
from lbrc_flask.database import db


def init_printing(app):
    pass

import re
import socket
import datetime
import time
from flask import current_app, flash


PRINTER_DEV = 'PRINTER_DEV'
PRINTER_CVRC_LAB_SAMPLE = 'PRINTER_CVRC_LAB_SAMPLE'
PRINTER_BRU_CRF_SAMPLE = 'PRINTER_BRU_CRF_SAMPLE'
PRINTER_BRU_CRF_BAG = 'PRINTER_BRU_CRF_BAG'
PRINTER_LIMB = 'PRINTER_LIMB'
PRINTER_TMF_SAMPLE = 'PRINTER_TMF_SAMPLE'
PRINTER_TMF_BAG = 'PRINTER_TMF_BAG'
PRINTER_ADDRESS = 'PRINTER_ADDRESS'

_POS_BAG_LEFT_COL = 100
_POS_TITLE_TOP = 100
_POS_CONTENT_TOP = _POS_TITLE_TOP + 100

_WIDTH_BAG = 1200
_HEIGHT_BAG = 1500
_WIDTH_SAMPLE = 600
_LINE_HEIGHT = 55
_TITLE_LINE_HEIGHT = 80


class Label:
    SMALLEST_FONT=80
    LARGEST_FONT=86

    FONT_TINY = 'P'
    FONT_SMALL = 'R'
    FONT_MEDIUM = 'T'
    FONT_LARGE = 'U'
    FONT_TITLE = 'V'

    _CODE_START = '^XA'
    _CODE_WIDTH = '^PW{width}'
    _CODE_NEXT_TEXT_CENTRED = '^FB{width},,,C'
    _CODE_TEXT = '^FO{x},{y}^A{font}^FD{text}^FS'
    _CODE_BARCODE =            '^BY{width},3,{height}^FT{x},{y}^BCN,,Y,N^FD{barcode}^FS'
    _CODE_BARCODE_LARGE_TEXT = '^BY{width},3,{height}^FT{x},{y}^AU^BCN,,Y,N^FD{barcode}^FS'
    _CODE_BARCODE_ROTATED =    '^BY{width},2.5,{height}^FT{x},{y}^AU^BCR,,Y,N^FD{barcode}^FS'
    _CODE_QUANTITY = '^PQ{quantity},0,1,Y'
    _CODE_END = '^XZ'

    WIDTH_BAG = _WIDTH_BAG
    WIDTH_SAMPLE = _WIDTH_SAMPLE
    HEIGHT_BAG = _HEIGHT_BAG

    def __init__(self, label_printer_set, width, height=0, duplicates=1, fonts=None, font_differential=0):
        self.fonts = fonts or {
            self.FONT_TINY: self.FONT_TINY,
            self.FONT_SMALL: self.FONT_SMALL,
            self.FONT_MEDIUM: self.FONT_MEDIUM,
            self.FONT_LARGE: self.FONT_LARGE,
            self.FONT_TITLE: self.FONT_TITLE,
        }

        self.width = width
        self.height = height
        self.duplicates = duplicates
        self.instructions = []
        self.label_printer_set = label_printer_set
        self.font_differential = font_differential
    
    def _get_font(self, size):
        return chr(min(Label.LARGEST_FONT, max(Label.SMALLEST_FONT, Label.SMALLEST_FONT + size - 1 + self.font_differential)))

    def get_code(self):
        code = []
        code.append(self._CODE_START)
        code.append(self._CODE_WIDTH.format(width=self.width))

        code.extend(self.instructions)

        code.append(self._CODE_QUANTITY.format(quantity=self.duplicates))
        code.append(self._CODE_END)

        return ''.join(code)
    
    def add(self, code):
        self.instructions.append(code)

    def add_next_text_centred(self, width=None):
        self.add(self._CODE_NEXT_TEXT_CENTRED.format(width=(width or self.width)))

    def add_text(self, text, x_pos, y_pos, font_size, centered=False):
        if centered:
            self.add_next_text_centred()

        self.add(self._CODE_TEXT.format(
                x=x_pos,
                y=y_pos,
                font=self._get_font(font_size),
                text=text,
            ))

    def add_title(self, **kwargs):
        self.add_text(font_size=7, **kwargs)

    def add_large_text(self, **kwargs):
        self.add_text(font_size=6, **kwargs)

    def add_medium_text(self, **kwargs):
        self.add_text(font_size=5, **kwargs)

    def add_small_text(self, **kwargs):
        self.add_text(font_size=4, **kwargs)

    def add_barcode(self, barcode, x_pos=0, y_pos=0, line_height=80, line_width=3, centered=False, rotated=False):
        if centered:
            x_pos = self._bar_code_centred_x(id=barcode, label_width=self.width)

        if rotated:
            code = self._CODE_BARCODE_ROTATED
        else:
            code = self._CODE_BARCODE

        self.add(code.format(
            width=line_width,
            x=x_pos,
            y=y_pos,
            height=line_height,
            barcode=self._encode_barcode(barcode),
        ))

    def add_barcode_large_text(self, barcode, x_pos=0, y_pos=0, line_height=80, line_width=3, centered=False):
        if centered:
            x_pos = self._bar_code_centred_x(id=barcode, label_width=self.width)

        self.add(self._CODE_BARCODE_LARGE_TEXT.format(
            width=line_width,
            x=x_pos,
            y=y_pos,
            height=line_height,
            barcode=self._encode_barcode(barcode),
        ))

    def add_version(self, version):
        self.add_text(
            text='v{version} printed {date}'.format(
                    version=version,
                    date=datetime.date.today().strftime("%d %B %Y"),
                ),
            x_pos=0,
            y_pos=self.height - 25,
            font_size=4,
            centered=True,
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

    def print_on_printer(self, printer):
        printer.print_label(self.get_code())


class SmallLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(width=Label.WIDTH_SAMPLE, height=0, **kwargs)

    def print(self):
        self.print_on_printer(self.label_printer_set.sample_printer)


class BarcodeLabel(SmallLabel):
    def __init__(self, barcode, title='', **kwargs):
        super().__init__(**kwargs)

        self.add_small_text(text=title, x_pos=20, y_pos=60)
        self.add_barcode_large_text(barcode=barcode, x_pos=20, y_pos=203)


class RecruitedNoticeLabel(SmallLabel):
    def __init__(self, study_name, **kwargs):
        super().__init__(**kwargs)

        self.add_medium_text(text='Patient recruited to research study:', x_pos=20, y_pos=30)
        self.add_medium_text(text=study_name, x_pos=20, y_pos=90)
        self.add_medium_text(text='Date Approached:', x_pos=20, y_pos=180)
        self.add_medium_text(text='Date Consented:', x_pos=20, y_pos=240)


class AliquotBottleLabel(SmallLabel):
    def __init__(self, barcode, **kwargs):
        super().__init__(**kwargs)

        self.add_barcode(barcode=barcode, x_pos=100, y_pos=30, line_width=2, rotated=True)
        self.add_barcode(barcode=barcode, x_pos=280, y_pos=30, line_width=2, rotated=True)
        self.add_barcode(barcode=barcode, x_pos=460, y_pos=30, line_width=2, rotated=True)


class BagSmallLabel(SmallLabel):
    def __init__(self, title, **kwargs):
        super().__init__(**kwargs)

        self.add_title(text=title, x_pos=0, y_pos=30)
        self.add_medium_text(text='Date:', x_pos=0, y_pos=120)
        self.add_medium_text(text='Time:', x_pos=0, y_pos=180)
        self.add_medium_text(text='Please affix participant ID label', x_pos=0, y_pos=240)


class LargeLabel(Label):
    _CODE_SIDE_BAR = '^FO1100,0^AVR^FD{side_bar}^FS'

    def __init__(self, **kwargs):
        super().__init__(width=Label.WIDTH_BAG, height=Label.HEIGHT_BAG, **kwargs)

    def print(self):
        self.print_on_printer(self.label_printer_set.bag_printer)

    def add_sidebar(self, text):
        self.add_next_text_centred(width=self.height)
        self.add(self._CODE_SIDE_BAR.format(side_bar=text))


class BagLargeLabel(LargeLabel):
    _CODE_FORM = '''
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

    def __init__(
        self,
        title,
        participant_id,
        version,
        subheaders=[],
        lines=[],
        warnings=[],
        subset='',
        sidebar='',
        form_date_text=None,
        form_time_text=None,
        form_emergency_text=None,
        form_consent_a_text=None,
        form_consent_b_text=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.add_title(text=title, x_pos=0, y_pos=_POS_TITLE_TOP, centered=True)
        self.add_sidebar(text=f'{sidebar} {subset}')

        y = _POS_CONTENT_TOP

        for sh in subheaders:
            if sh.startswith('* '):
                self.add_large_text(text=sh, x_pos=_POS_BAG_LEFT_COL, y_pos=y, centered=False)
            else:
                self.add_large_text(text=sh, x_pos=0, y_pos=y, centered=True)
            y += _LINE_HEIGHT

        if subheaders:
            y += _LINE_HEIGHT

        for l in lines:
            self.add_large_text(text=l, x_pos=0, y_pos=y, centered=True)
            y += _LINE_HEIGHT

        if lines:
            y += _LINE_HEIGHT

        for w in warnings:
            y += _LINE_HEIGHT
            self.add_large_text(text=w, x_pos=0, y_pos=y, centered=True)
            y += _LINE_HEIGHT

        self.add(
            self._CODE_FORM.format(
                str_date=form_date_text or 'Date',
                str_time_sample_taken=form_time_text or 'Time Sample Taken',
                str_emergency_consent=form_emergency_text or 'Emergency Consent',
                str_full_consent=form_consent_a_text or 'Full Consent',
                str_full_consent_b=form_consent_b_text or '',
                font=self._get_font(5),
            )
        )

        self.add_barcode(barcode=participant_id, y_pos=1400, centered=True)
        self.add_version(version)


class MedicalNotesStandardLabel(LargeLabel):
    _CODE_FORM = '''
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

    def __init__(
        self,
        study_a,
        chief_investigator,
        chief_investigator_email,
        study_sponsor,
        iras_id,
        version,
        participant_id,
        study_b='',
        **kwargs,
    ):
        super().__init__(**kwargs)

        y = _POS_TITLE_TOP

        self.add_medium_text(text='Participant in the following research study:', x_pos=0, y_pos=y, centered=True)

        y += _TITLE_LINE_HEIGHT

        self.add_title(text=study_a, x_pos=0, y_pos=y, centered=True)

        y += _TITLE_LINE_HEIGHT

        self.add_title(text=study_b, x_pos=0, y_pos=y, centered=True)

        y += _TITLE_LINE_HEIGHT
        y += _TITLE_LINE_HEIGHT

        self.add_medium_text(text=f'Participant ID: {participant_id}', x_pos=_POS_BAG_LEFT_COL, y_pos=y)

        y += _LINE_HEIGHT

        self.add_medium_text(text=f'Chief Investigator (CI): {chief_investigator}', x_pos=_POS_BAG_LEFT_COL, y_pos=y)

        y += _LINE_HEIGHT

        self.add_medium_text(text=f'CI Email: {chief_investigator_email}', x_pos=_POS_BAG_LEFT_COL, y_pos=y)

        y += _LINE_HEIGHT

        self.add_medium_text(text=f'Study Sponsor: {study_sponsor}', x_pos=_POS_BAG_LEFT_COL, y_pos=y)

        y += _LINE_HEIGHT

        self.add_medium_text(text=f'IRAS ID: {iras_id}', x_pos=_POS_BAG_LEFT_COL, y_pos=y)

        self.add(
            self._CODE_FORM.format(font=self._get_font(5))
        )
    
        self.add_version(version)


class LabelPrinter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hostname_or_ip_address = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.name

    def print_label(self, printer_code):
        if self.hostname_or_ip_address in current_app.config:
            host = current_app.config[self.hostname_or_ip_address]
        else:
            host = self.hostname_or_ip_address

        if current_app.config['TESTING']:
            flash('Testing, not printing')
            #current_app.logger.info(f'Fake print of {printer_code} to host {host}')
            current_app.logger.info(f'.')
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, 9100))
                s.sendall(printer_code.encode('ascii'))
            time.sleep(0.1)


class LabelPrinterSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bag_printer_id = db.Column(db.Integer, db.ForeignKey(LabelPrinter.id))
    bag_printer = db.relationship(LabelPrinter, foreign_keys=[bag_printer_id])
    sample_printer_id = db.Column(db.Integer, db.ForeignKey(LabelPrinter.id))
    sample_printer = db.relationship(LabelPrinter, foreign_keys=[sample_printer_id])

    def __repr__(self):
        return self.name


class LabelBundle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id))
    study = db.relationship(Study, backref=db.backref("label_bundles"))
    participant_id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    participant_id_provider = db.relationship(IdProvider, foreign_keys=[participant_id_provider_id])
    label_printer_set_id = db.Column(db.Integer, db.ForeignKey(LabelPrinterSet.id))
    label_printer_set = db.relationship(LabelPrinterSet)
    disable_batch_printing = db.Column(db.Boolean)
    print_recruited_notice = db.Column(db.Boolean)
    user_defined_participant_id = db.Column(db.Boolean)
    participant_label_count = db.Column(db.Integer)
    sidebar_prefix = db.Column(db.String(50), default='')

    def __repr__(self):
        return f'{self.study.name}: {self.name}'

    def get_labels(self, count):
        labels = []

        for _ in range(count):
            labels.extend(self.get_label_bundle())

        return labels

    def study_name(self):
        return f'{self.sidebar_prefix} {self.study.name}'.strip()

    def set_participant_id(self, participant_id):
        self._set_participant_id = participant_id

    def _get_participant_id(self):
        if getattr(self, '_set_participant_id', None):
            return self._set_participant_id
        else:
            return self.participant_id_provider.allocate_id().barcode

    def get_label_bundle(self):
        labels = []

        participant_id = self._get_participant_id()

        for bs in self.bags:
            labels.extend(bs.get_labels(participant_id))
        
        for ab in self.aliquot_batches:
            labels.extend(ab.get_labels())

        if self.print_recruited_notice:
            labels.append(RecruitedNoticeLabel(study_name=self.study_name(), label_printer_set=self.label_printer_set))

        if self.medical_notes_label:
            labels.extend(self.medical_notes_label.get_labels(participant_id))
        
        if self.participant_label_count > 0:
            labels.append(BarcodeLabel(participant_id, label_printer_set=self.label_printer_set, duplicates=self.participant_label_count))

        return labels


class SampleBagLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_num = db.Column(db.Integer, nullable=False)
    label_bundle_id = db.Column(db.Integer, db.ForeignKey(LabelBundle.id))
    label_bundle = db.relationship(LabelBundle, backref=db.backref("bags"))
    title = db.Column(db.String(100), nullable=False)
    visit = db.Column(db.String(100), nullable=False, default='')
    subheaders = db.Column(db.Text, nullable=False, default='')
    warnings = db.Column(db.Text, nullable=False, default='')
    small_format = db.Column(db.Boolean, nullable=False, default=False)
    do_not_print_bag = db.Column(db.Boolean, nullable=False, default=False)
    form_date_text = db.Column(db.String(100), nullable=False, default='')
    form_time_text = db.Column(db.String(100), nullable=False, default='')
    form_emergency_text = db.Column(db.String(100), nullable=False, default='')
    form_consent_a_text = db.Column(db.String(100), nullable=False, default='')
    form_consent_b_text = db.Column(db.String(100), nullable=False, default='')
    font_differential = db.Column(db.Integer, nullable=False, default=0)

    __mapper_args__ = {
        "version_id_col": version_num,
    }

    def _label_printer_set(self):
        return self.label_bundle.label_printer_set

    def get_labels(self, participant_id):
        labels = []

        if not self.do_not_print_bag:
            if self.small_format:
                labels.append(BagSmallLabel(title=self.title, label_printer_set=self._label_printer_set()))
            else:
                labels.append(BagLargeLabel(
                    title=self.title,
                    participant_id=participant_id,
                    subset=self.visit,
                    sidebar=self.label_bundle.study_name(),
                    lines=[f'{s.count} x {s.name}' for s in self.samples if s.print_on_bag],
                    version=self.version_num,
                    subheaders=self.subheaders.splitlines(),
                    warnings=self.warnings.splitlines(),
                    label_printer_set=self._label_printer_set(),
                    font_differential=self.font_differential,
                    form_date_text=self.form_date_text,
                    form_time_text=self.form_time_text,
                    form_emergency_text=self.form_emergency_text,
                    form_consent_a_text=self.form_consent_a_text,
                    form_consent_b_text=self.form_consent_b_text,
                ))

        for s in self.samples:
            labels.extend(s.get_labels(self.visit))
        
        return labels


class MedicalNotesLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_num = db.Column(db.Integer, nullable=False)
    label_bundle_id = db.Column(db.Integer, db.ForeignKey(LabelBundle.id))
    label_bundle = db.relationship(LabelBundle, backref=db.backref("medical_notes_label", uselist=False))
    study_name_line_1 = db.Column(db.String(100), nullable=False)
    study_name_line_2 = db.Column(db.String(100), nullable=False)
    chief_investigator = db.Column(db.String(100), nullable=False)
    chief_investigator_email = db.Column(db.String(100), nullable=False)
    study_sponsor = db.Column(db.String(100), nullable=False)
    iras_id = db.Column(db.String(100), nullable=False)

    __mapper_args__ = {
        "version_id_col": version_num,
    }

    def _label_printer_set(self):
        return self.label_bundle.label_printer_set

    def get_labels(self, participant_id):
        return [MedicalNotesStandardLabel(
            study_a=self.study_name_line_1,
            study_b=self.study_name_line_2,
            chief_investigator=self.chief_investigator,
            chief_investigator_email=self.chief_investigator_email,
            study_sponsor=self.study_sponsor,
            iras_id=self.iras_id,
            version=self.version_num,
            participant_id=participant_id,
            label_printer_set=self._label_printer_set(),
        )]


class SampleLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_bag_label_id = db.Column(db.Integer, db.ForeignKey(SampleBagLabel.id))
    sample_bag_label = db.relationship(SampleBagLabel, backref=db.backref("samples"))
    id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    id_provider = db.relationship(IdProvider, foreign_keys=[id_provider_id])
    name = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, nullable=False, default=1)
    duplicates = db.Column(db.Integer, nullable=False, default=1)
    duplicate_names = db.Column(db.Text, nullable=True)
    print_on_bag = db.Column(db.Boolean, nullable=False, default=False)

    def _label_printer_set(self):
        return self.sample_bag_label._label_printer_set()

    def _duplicate_names(self):
        return (self.duplicate_names or '').splitlines()

    def get_labels(self, visit=''):
        labels = []

        for _ in range(self.count):
            title = f'{visit} {self.name}'.strip()

            if self.duplicates > 1 and len(self._duplicate_names()) > 0:
                for title, dup_name in zip_longest([title] * self.duplicates, self._duplicate_names(), fillvalue=''):
                    labels.append(BarcodeLabel(
                        barcode=self.id_provider.allocate_id().barcode,
                        title=f'{title} {dup_name}'.strip(),
                        label_printer_set=self._label_printer_set(),
                    ))
            else:
                labels.append(BarcodeLabel(
                    barcode=self.id_provider.allocate_id().barcode,
                    title=title,
                    label_printer_set=self._label_printer_set(),
                    duplicates=self.duplicates,
                ))

        return labels


class AliquotBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label_bundle_id = db.Column(db.Integer, db.ForeignKey(LabelBundle.id))
    label_bundle = db.relationship(LabelBundle, backref=db.backref("aliquot_batches"))
    id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    id_provider = db.relationship(IdProvider, foreign_keys=[id_provider_id])

    def _label_printer_set(self):
        return self.label_bundle.label_printer_set

    def get_labels(self):
        labels = []

        if len(self.aliquots) > 0:
            aliquot_id = self.id_provider.allocate_id().id

            for a in self.aliquots:
                labels.extend(a.get_labels(aliquot_id))
            
        return labels


class AliquotLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aliquot_batch_id = db.Column(db.Integer, db.ForeignKey(AliquotBatch.id))
    aliquot_batch = db.relationship(AliquotBatch, backref=db.backref("aliquots"))
    prefix = db.Column(db.String(10), nullable=False)
    count = db.Column(db.Integer, nullable=False, default=1)

    def _label_printer_set(self):
        return self.aliquot_batch._label_printer_set()

    def get_labels(self, aliquot_id):
        labels = []

        if self.count > 1:
            for i in range(1, self.count + 1):
                labels.append(AliquotBottleLabel(
                    barcode=f'{self.prefix}{aliquot_id}-{i}',
                    label_printer_set=self._label_printer_set(),
                ))
        else:
            labels.append(AliquotBottleLabel(
                barcode=f'{self.prefix}{aliquot_id}',
                label_printer_set=self._label_printer_set(),
            ))

        return labels
