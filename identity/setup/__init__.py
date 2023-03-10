from lbrc_flask.database import db
from identity.printing import LabelPrinter, LabelPrinterSet
from identity.printing import PRINTER_BRU_CRF_BAG, PRINTER_BRU_CRF_SAMPLE, PRINTER_CVRC_LAB_SAMPLE, PRINTER_DEV, PRINTER_LIMB, PRINTER_TMF_BAG, PRINTER_TMF_SAMPLE


def setup_data():
    _create_printer_sets()


_printer_sets = [
    {
        'name': 'Development',
        'bag_printer_name':  'Dev Bag',
        'bag_printer_host':  PRINTER_DEV,
        'sample_printer_name': 'Dev Sample',
        'sample_printer_host': PRINTER_DEV,
    },
    {
        'name': 'CV Lab',
        'bag_printer_name':  'CV Lab Bag',
        'bag_printer_host':  PRINTER_CVRC_LAB_SAMPLE,
        'sample_printer_name': 'CV Lab Sample',
        'sample_printer_host': PRINTER_CVRC_LAB_SAMPLE,
    },
    {
        'name': 'CV BRU2',
        'bag_printer_name':  'CV BRU2 Bag Printer',
        'bag_printer_host':  PRINTER_BRU_CRF_BAG,
        'sample_printer_name': 'CV BRU2 Sample Printer',
        'sample_printer_host': PRINTER_BRU_CRF_SAMPLE,
    },
    {
        'name': 'CV LIMB',
        'bag_printer_name':  'CV LIMB Bag',
        'bag_printer_host':  PRINTER_LIMB,
        'sample_printer_name': 'CV LIMB Sample',
        'sample_printer_host': PRINTER_LIMB,
    },
    {
        'name': 'CV TMF',
        'bag_printer_name':  'CV TMF Bag Printer',
        'bag_printer_host':  PRINTER_TMF_BAG,
        'sample_printer_name': 'CV TMF Sample Printer',
        'sample_printer_host': PRINTER_TMF_SAMPLE,
    },
]
def _create_printer_sets():
    for p in _printer_sets:
        s = LabelPrinterSet.query.filter_by(name=p['name']).first()

        if s:
            continue

        bag_printer = LabelPrinter.query.filter_by(name=p['bag_printer_name']).first()

        if not bag_printer:
            bag_printer = LabelPrinter(name=p['bag_printer_name'], hostname_or_ip_address=p['bag_printer_host'])

        sample_printer = LabelPrinter.query.filter_by(name=p['sample_printer_name']).first()

        if not sample_printer:
            sample_printer = LabelPrinter(name=p['sample_printer_name'], hostname_or_ip_address=p['sample_printer_host'])

        s = LabelPrinterSet(
            name=p['name'],
            bag_printer=bag_printer,
            sample_printer=sample_printer,
        )

        db.session.add(s)
    
    db.session.commit()
