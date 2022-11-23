from lbrc_flask.database import db
from identity.model.id import IdProvider, ParticipantIdentifierType
from lbrc_flask.security import get_system_user, get_admin_user
from flask import current_app
from lbrc_flask.python_helpers import get_concrete_classes
from identity.printing import LabelBatch, LabelPrinter, LabelPrinterSet, SampleBagLabel, SampleLabel
from identity.printing.model import PRINTER_BRU_CRF_BAG, PRINTER_BRU_CRF_SAMPLE, PRINTER_CVRC_LAB_SAMPLE, PRINTER_DEV, PRINTER_LIMB, PRINTER_TMF_BAG, PRINTER_TMF_SAMPLE, LabelPack
from identity.model import Study
from collections import ChainMap
from itertools import chain
from identity.model.id import (
    SequentialIdProvider,
    LegacyIdProvider,
    PseudoRandomIdProvider,
    BioresourceIdProvider,
    StudyIdSpecification,
    ParticipantIdentifierType,
)
from identity.setup.studies import StudyName


def setup_data():
    user = get_system_user()
    
    _setup_participant_identifier_types(user)

    create_providers(user)
    create_studies(user)
    create_label_packs(user)

    _create_printer_sets()
    _create_label_batches()


def _setup_participant_identifier_types(user):
    if ParticipantIdentifierType.query.filter_by(name=ParticipantIdentifierType.STUDY_PARTICIPANT_ID).count() > 0:
        return
    
    db.session.add(ParticipantIdentifierType(
        name=ParticipantIdentifierType.STUDY_PARTICIPANT_ID,
        last_updated_by_user_id=user.id,
    ))
    db.session.commit()


def create_label_packs(user):
    current_app.logger.info(f'Creating Label Packs')

    for x in get_concrete_classes(LabelPack):

        if LabelPack.query.filter_by(type=x.__class__.__name__).count() == 0:
            current_app.logger.info(f'Creating {x.name}')

            x.study = Study.query.filter_by(name=x.__study_name__['name']).first()

            db.session.add(x)

    db.session.commit()


def create_providers(user):
    current_app.logger.info(f'Creating Providers')

    for prefix, name in ChainMap({}, *chain.from_iterable([x.pseudo_identifier_types for x in get_concrete_classes(StudyIdSpecification)])).items():
        if PseudoRandomIdProvider.query.filter_by(name=name).count() == 0:
            current_app.logger.info(f'Creating provider {name}')
            db.session.add(PseudoRandomIdProvider(
                name=name,
                prefix=prefix,
            ))

    for prefix, name in ChainMap({}, *chain.from_iterable([x.legacy_identifier_types for x in get_concrete_classes(StudyIdSpecification)])).items():
        if LegacyIdProvider.query.filter_by(name=name).count() == 0:
            current_app.logger.info(f'Creating provider {name}')
            db.session.add(LegacyIdProvider(
                name=name,
                prefix=prefix,
                number_fixed_length=8,
            ))

    for params in chain.from_iterable([x.sequential_identifier_types for x in get_concrete_classes(StudyIdSpecification)]):
        if SequentialIdProvider.query.filter_by(name=params['name']).count() == 0:
            current_app.logger.info(f'Creating provider {params["name"]}')
            db.session.add(SequentialIdProvider(
                **params,
            ))

    for prefix, name in ChainMap({}, *chain.from_iterable([x.bioresource_identifier_types for x in get_concrete_classes(StudyIdSpecification)])).items():
        if BioresourceIdProvider.query.filter_by(name=name).count() == 0:
            current_app.logger.info(f'Creating provider {name}')
            db.session.add(BioresourceIdProvider(
                name=name,
                prefix=prefix,
            ))

    db.session.commit()


def create_studies(user):
    current_app.logger.info(f'Creating Studies')

    for s in StudyName().all_studies():
        study_name = s['name']
        study = Study.query.filter_by(name=study_name).first()

        if not study:
            current_app.logger.info(f'Creating Study {study_name}')

            study = Study(name=study_name)
            db.session.add(study)

        admin = get_admin_user()
        admin.studies.append(study)
        db.session.add(admin)

    db.session.commit()

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


_label_batches = [
    {
        'name': 'Alleviate',
        'study':  StudyName.ALLEVIATE,
        'participant_id_prefix': 'AllPt',
        'sample_id_prefix': 'AllPt',
        'aliquot_id_prefix': '',
        'printer_set_name': 'CV TMF',
        'disable_batch_printing': False,
        'print_recruited_notice': False,
        'participant_label_count': 35,
        'visits': ['Baseline', '12 Weeks'],
        'bags': [
            {
                'title': 'ALLEVIATE (room temp)',
                'small_format': False,
                'subheaders': '',
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'name': '4.9ml Serum (brown)',
                        'count': 1,
                    },
                    {
                        'name': '2.7ml EDTA (purple)',
                        'count': 1,
                    },
                ],
            },
            {
                'title': 'ALLEVIATE (on ice)',
                'small_format': False,
                'subheaders': '',
                'warnings': 'Put on ice\nTransfer to lab within 90 minutes',
                'samples': [
                    {
                        'name': '4.9ml Litium Hep. (orange)',
                        'count': 2,
                    },
                    {
                        'name': '4.9ml EDTA (pink)',
                        'count': 1,
                    },
                ],
            },
        ],
    },
    {
        'name': 'Bioresource Pack',
        'study':  StudyName.Bioresource,
        'participant_id_prefix': 'BR',
        'sample_id_prefix': '',
        'aliquot_id_prefix': '',
        'printer_set_name': 'CV BRU2 Bag Printer',
        'disable_batch_printing': False,
        'print_recruited_notice': False,
        'participant_label_count': 1,
        'visits': [''],
        'bags': [],
    },
]
def _create_label_batches():
    for lb in _label_batches:
        if LabelBatch.query.filter_by(name=lb['name']).one_or_none():
            continue

        batch = LabelBatch(
            name=lb['name'],
            study=Study.query.filter_by(name=lb['study']['name']).one(),
            participant_id_provider=IdProvider.query.filter_by(prefix=lb['participant_id_prefix']).one_or_none(),
            sample_id_provider=IdProvider.query.filter_by(prefix=lb['sample_id_prefix']).one_or_none(),
            aliquot_id_provider=IdProvider.query.filter_by(prefix=lb['sample_id_prefix']).one_or_none(),
            label_printer_set=LabelPrinterSet.query.filter_by(name=lb['printer_set_name']).one_or_none(),
            disable_batch_printing=lb['disable_batch_printing'],
            print_recruited_notice=lb['print_recruited_notice'],
            participant_label_count=lb['participant_label_count'],
        )

        for b in lb['bags']:
            for v in lb['visits']:
                bag = SampleBagLabel(
                    label_batch = batch,
                    title=b['title'],
                    visit=v,
                    subheaders=b['subheaders'],
                    warnings=b['warnings'],
                    small_format=b['small_format'],
                )

                db.session.add(bag)

                for s in b['samples']:
                    db.session.add(SampleLabel(
                        sample_bag_label=bag,
                        name=s['name'],
                        count=s['count'],
                    ))

        db.session.add(batch)
    
    db.session.commit()
