import re
import socket
import datetime
import time
from collections import namedtuple
from flask import current_app
from flask_login import current_user
from ..database import db
from identity.model.id import (
    Study,
    ParticipantIdentifierType,
)

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


def print_label(host, printer_code, port=9100):
    if current_app.config['TESTING']:
        #current_app.logger.info(f'Fake print of {printer_code} to host {host}')
        current_app.logger.info(f'.')
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((current_app.config[host], port))
            s.sendall(printer_code.encode('ascii'))
        time.sleep(0.1)


def print_barcode(printer, barcode, count=1, title=''):
    code = ''.join([
        _CODE_START,
        _CODE_WIDTH.format(width=_WIDTH_SAMPLE),
        _CODE_TEXT.format(
            x=50,
            y=60,
            font=FONT_SMALL,
            text=title,
        ),
        _CODE_BARCODE_LARGE_TEXT.format(
            width=3,
            x=50,
            y=203,
            height=80,
            barcode=_encode_barcode(barcode),
        ),
        _CODE_QUANTITY.format(quantity=count),
        _CODE_END,
    ])

    print_label(
        host=printer,
        printer_code=code,
    )


def _encode_barcode(barcode):
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


def print_sample(label_context, count=1, title=''):
    print_barcode(
        printer=label_context.sample_printer,
        barcode=label_context.sample_id_provider.allocate_id(current_user).barcode,
        count=count,
        title=title,
    )


def print_recruited_notice(printer, study_name, count=1):
    code = ''.join([
        _CODE_START,
        _CODE_WIDTH.format(width=_WIDTH_SAMPLE),
        _CODE_TEXT.format(
            x=20,
            y=30,
            font=FONT_MEDIUM,
            text='Patient recruited to research study:',
        ),
        _CODE_TEXT.format(
            x=20,
            y=90,
            font=FONT_TITLE,
            text=study_name,
        ),
        _CODE_TEXT.format(
            x=20,
            y=180,
            font=FONT_MEDIUM,
            text='Date Approached:',
        ),
        _CODE_TEXT.format(
            x=20,
            y=240,
            font=FONT_MEDIUM,
            text='Date Consented:',
        ),
        _CODE_QUANTITY.format(quantity=count),
        _CODE_END,
    ])

    print_label(
        host=printer,
        printer_code=code,
    )


def print_aliquot(printer, barcode, count=1):
    code = ''.join([
        _CODE_START,
        _CODE_BARCODE_ROTATED.format(
            width=2,
            x=100,
            y=30,
            height=80,
            barcode=barcode,
        ),
        _CODE_BARCODE_ROTATED.format(
            width=2,
            x=280,
            y=30,
            height=80,
            barcode=barcode,
        ),
        _CODE_BARCODE_ROTATED.format(
            width=2,
            x=460,
            y=30,
            height=80,
            barcode=barcode,
        ),
        _CODE_QUANTITY.format(quantity=count),
        _CODE_END,
    ])

    print_label(
        host=printer,
        printer_code=code,
    )


def print_bag(
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
    code = [
        _CODE_START,
        _CODE_WIDTH.format(width=_WIDTH_BAG),
        _CODE_NEXT_TEXT_CENTRED.format(width=_WIDTH_BAG),
        _CODE_TEXT.format(
            x=0,
            y=_POS_TITLE_TOP,
            font=label_context.FONT_TITLE,
            text=title,
        ),
        _CODE_NEXT_TEXT_CENTRED.format(width=_HEIGHT_BAG),
        _CODE_SIDE_BAR.format(side_bar=label_context.side_bar + ' ' + subset),
    ]

    y = _POS_CONTENT_TOP

    for sh in subheaders:
        code.extend([
            _CODE_NEXT_TEXT_CENTRED.format(width=_WIDTH_BAG),
            _CODE_TEXT.format(
                x=0,
                y=y,
                font=label_context.FONT_LARGE,
                text=sh,
            ),
        ])

        y += _LINE_HEIGHT

    if subheaders:
        y += _LINE_HEIGHT

    for l in lines:
        code.extend([
            _CODE_TEXT.format(
                x=_POS_BAG_LEFT_COL,
                y=y,
                font=label_context.FONT_MEDIUM,
                text=l,
            ),
        ])

        y += _LINE_HEIGHT

    if lines:
        y += _LINE_HEIGHT

    for w in warnings:

        y += _LINE_HEIGHT

        code.extend([
            _CODE_NEXT_TEXT_CENTRED.format(width=_WIDTH_BAG),
            _CODE_TEXT.format(
                x=0,
                y=y,
                font=label_context.FONT_LARGE,
                text=w,
            ),
        ])

        y += _LINE_HEIGHT


    code.extend([
        _CODE_BAG_FORM.format(
            str_date=str_date,
            str_time_sample_taken=str_time_sample_taken,
            str_emergency_consent=str_emergency_consent,
            str_full_consent=str_full_consent,
            str_full_consent_b=str_full_consent_b,
            font=label_context.FONT_MEDIUM,
        ),
        _CODE_BARCODE.format(
            width=3,
            x=bar_code_centred_x(id=label_context.participant_id, label_width=_WIDTH_BAG),
            y=1400,
            height=80,
            barcode=_encode_barcode(label_context.participant_id),
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
        _CODE_QUANTITY.format(quantity=count),
        _CODE_END,
    ])

    print_label(
        host=label_context.bag_printer,
        printer_code=''.join(code),
    )


def print_bag_small(
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

    print_label(
        host=printer,
        printer_code=''.join(code),
    )


def bar_code_centred_x(id, label_width):
    bar_code_width = (len(id) * 16) + 120
    return (label_width - bar_code_width) // 2


def print_notes_label(
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

    print_label(
        host=label_context.bag_printer,
        printer_code=''.join(code),
    )
