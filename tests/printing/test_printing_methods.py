import pytest
from unittest.mock import patch, MagicMock
from identity.model.id import FixedIdProvider
from identity.printing.printing_methods import (
    print_label,
    print_barcode,
    _encode_barcode,
    print_sample,
    print_recruited_notice,
    print_aliquot,
    print_bag,
    print_bag_small,
    print_notes_label,
)
from identity.printing.model import (
    SampleContext,
    BagContext,
)


@pytest.yield_fixture(scope="function")
def mock_socket(app):
    with patch('identity.printing.printing_methods.socket') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_print_label(app):
    with patch('identity.printing.printing_methods.print_label') as mock:
        yield mock


@pytest.yield_fixture(scope="function")
def mock_print_barcode(app):
    with patch('identity.printing.printing_methods.print_barcode') as mock:
        yield mock


def test__print_label__testing(app, faker, mock_socket):
    print_label('test host', 'printer code')

    mock_socket.socket.assert_not_called()


def test__print_label__not_testing(app, faker, mock_socket):
    app.config['TESTING'] = False
    app.config['host'] = 'Host actual'

    s = MagicMock(name='Fred')
    mock_socket.socket.return_value.__enter__.return_value = s

    print_label('host', 'printer code')

    mock_socket.socket.assert_called_once()
    s.connect.assert_called_once_with(('Host actual', 9100))
    s.sendall.assert_called_once_with('printer code'.encode('ascii'))


@pytest.mark.parametrize(
    "count",
    [
        (1),
        (10),
    ],
)
def test__print_barcode(app, faker, mock_print_label, count):
    print_barcode('printer', 'barcode', count, 'title')

    mock_print_label.assert_called_once()


@pytest.mark.parametrize(
    "barcode, expected",
    [
        ('BPt123456', '>:BPt>5123456>6'),
        ('BPt1234567', '>:BPt>5123456>67'),
        ('BPt123456A', '>:BPt>5123456>6A'),
        ('BPt1234567A', '>:BPt>5123456>67A'),
        ('BPt1234567A1', '>:BPt>5123456>67A>5>61'),
        ('BPt1234567A1234', '>:BPt>5123456>67A>51234>6'),
    ],
)
def test__encode_barcode(app, faker, barcode, expected):
    actual = _encode_barcode(barcode)

    assert actual == expected


def test__print_sample__with_defaults(app, faker, mock_print_barcode):
    EXPECTED_PRINTER = faker.pystr()
    EXPECTED_ID = faker.pystr()

    context = SampleContext(printer=EXPECTED_PRINTER, id_provider=FixedIdProvider(EXPECTED_ID))

    print_sample(label_context=context)

    mock_print_barcode.assert_called_once_with(
        printer=EXPECTED_PRINTER,
        barcode=EXPECTED_ID,
        count=1,
        title='',
    )


def test__print_sample__without_defaults(app, faker, mock_print_barcode):
    EXPECTED_PRINTER = faker.pystr()
    EXPECTED_ID = faker.pystr()
    EXPECTED_TITLE = faker.pystr()
    EXPECTED_COUNT= faker.pyint(min_value=1)

    context = SampleContext(printer=EXPECTED_PRINTER, id_provider=FixedIdProvider(EXPECTED_ID))

    print_sample(label_context=context, count=EXPECTED_COUNT, title=EXPECTED_TITLE)

    mock_print_barcode.assert_called_once_with(
        printer=EXPECTED_PRINTER,
        barcode=EXPECTED_ID,
        count=EXPECTED_COUNT,
        title=EXPECTED_TITLE,
    )


@pytest.mark.parametrize(
    "count",
    [
        (1),
        (10),
    ],
)
def test__print_recruited_notice(app, faker, mock_print_label, count):
    print_recruited_notice('printer', 'barcode', count)

    mock_print_label.assert_called_once()


@pytest.mark.parametrize(
    "count",
    [
        (1),
        (10),
    ],
)
def test__print_aliquot(app, faker, mock_print_label, count):
    print_aliquot('printer', 'barcode', count)

    mock_print_label.assert_called_once()


def test__print_bag__with_defaults(app, faker, mock_print_label):
    EXPECTED_PRINTER = faker.pystr()
    EXPECTED_ID = faker.pystr()
    EXPECTED_SIDEBAR = faker.pystr()
    EXPECTED_TITLE = faker.pystr()
    EXPECTED_VERSION = faker.pystr()

    context = BagContext(printer=EXPECTED_PRINTER, participant_id=EXPECTED_ID, side_bar=EXPECTED_SIDEBAR)

    print_bag(
        label_context=context,
        title=EXPECTED_TITLE,
        version=EXPECTED_VERSION,
    )

    mock_print_label.assert_called_once()


@pytest.mark.parametrize(
    "count",
    [
        (1),
        (10),
    ],
)
def test__print_bag__without_defaults(app, faker, mock_print_label, count):
    context = BagContext(printer=faker.pystr(), participant_id=faker.pystr(), side_bar=faker.pystr())

    print_bag(
        label_context=context,
        title=faker.pystr(),
        version=faker.pystr(),
        subheaders=faker.pylist(10, False, ['str']),
        lines=faker.pylist(10, False, ['str']),
        warnings=faker.pylist(10, False, ['str']),
        subset=faker.pystr(),
        count=count,
        str_date=faker.pystr(),
        str_time_sample_taken=faker.pystr(),
        str_emergency_consent=faker.pystr(),
        str_full_consent=faker.pystr(),
        str_full_consent_b=faker.pystr(),
    )

    mock_print_label.assert_called_once()


@pytest.mark.parametrize(
    "count",
    [
        (1),
        (10),
    ],
)
def test__print_bag_small(app, faker, mock_print_label, count):
    print_bag_small(
        printer=faker.pystr(),
        title=faker.pystr(),
        line_1=faker.pystr(),
        line_2=faker.pystr(),
        count=count,
    )

    mock_print_label.assert_called_once()


@pytest.mark.parametrize(
    "count",
    [
        (1),
        (10),
    ],
)
def test__print_notes_label(app, faker, mock_print_label, count):
    context = BagContext(printer=faker.pystr(), participant_id=faker.pystr(), side_bar=faker.pystr())

    print_notes_label(
        label_context=context,
        study_a=faker.pystr(),
        study_b=faker.pystr(),
        chief_investigator=faker.pystr(),
        chief_investigator_email=faker.company_email(),
        study_sponsor=faker.pystr(),
        iras_id=faker.pystr(),
        version=faker.pystr(),
        participant_id=faker.pystr(),
    )

    mock_print_label.assert_called_once()
