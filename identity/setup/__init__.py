from lbrc_flask.database import db
from identity.model.id import IdProvider, ParticipantIdentifierType
from lbrc_flask.security import get_system_user, get_admin_user
from flask import current_app
from lbrc_flask.python_helpers import get_concrete_classes
from identity.printing import LabelBundle, LabelPrinter, LabelPrinterSet, SampleBagLabel, SampleLabel
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
    _create_label_bundles()


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


_label_bundles = [
    {
        'name': 'Alleviate',
        'study':  StudyName.ALLEVIATE,
        'participant_id_prefix': 'AllPt',
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
                        'id_prefix': 'AllPt',
                        'name': '4.9ml Serum (brown)',
                        'count': 1,
                        'print_on_bag': True,
                    },
                    {
                        'id_prefix': 'AllPt',
                        'name': '2.7ml EDTA (purple)',
                        'count': 1,
                        'print_on_bag': True,
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
                        'id_prefix': 'AllPt',
                        'name': '4.9ml Litium Hep. (orange)',
                        'count': 2,
                        'print_on_bag': True,
                    },
                    {
                        'id_prefix': 'AllPt',
                        'name': '4.9ml EDTA (pink)',
                        'count': 1,
                        'print_on_bag': True,
                    },
                ],
            },
        ],
    },
    {
        'name': 'Bioresource Pack',
        'study':  StudyName.Bioresource,
        'participant_id_prefix': 'BR',
        'printer_set_name': 'CV BRU2',
        'disable_batch_printing': False,
        'print_recruited_notice': False,
        'participant_label_count': 1,
        'visits': [],
        'bags': [],
    },
    {
        'name': 'Brave Pack',
        'study':  StudyName.BRAVE,
        'participant_id_prefix': 'BavPt',
        'printer_set_name': 'CV BRU2',
        'disable_batch_printing': False,
        'print_recruited_notice': False,
        'participant_label_count': 0,
        'visits': [],
        'bags': [
            {
                'title': 'Citrate and EDTA Bag',
                'small_format': False,
                'subheaders':   '* Fill citrate bottle 2nd\n'
                                '* Fill EDTA bottles 3rd and 4th\n'
                                '* Put citrate and EDTA on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_prefix': 'BavSa',
                        'name': '4.3ml Citrate',
                        'count': 1,
                        'print_on_bag': True,
                    },
                    {
                        'id_prefix': 'BavSa',
                        'name': '7.5ml EDTA',
                        'count': 2,
                        'print_on_bag': True,
                    },
                    {
                        'id_prefix': 'BavFm',
                        'name': '',
                        'count': 1,
                        'duplicates': 7,
                        'print_on_bag': False,
                    },
                ],
            },
            {
                'title': 'Serum and EDTA Bag',
                'small_format': False,
                'subheaders':   '* Fill serum bottle 1st\n'
                                '* Return to bag\n'
                                '* Fill the 2.7ml EDTA bottle 5th\n'
                                '* Return to bag',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_prefix': 'BavSa',
                        'name': '2.7ml EDTA',
                        'count': 1,
                        'print_on_bag': True,
                    },
                    {
                        'id_prefix': 'BavSa',
                        'name': '7.5ml Serum',
                        'count': 1,
                        'print_on_bag': True,
                    },
                ],
            },
        ],
    },
    {
        'name': 'Brave External Pack',
        'study':  StudyName.BRAVE,
        'participant_id_prefix': 'BavXPt',
        'printer_set_name': 'CV BRU2',
        'disable_batch_printing': False,
        'print_recruited_notice': False,
        'participant_label_count': 0,
        'visits': ['External'],
        'bags': [
            {
                'title': 'EDTA Bag',
                'small_format': False,
                'subheaders':   '',
                'warnings': 'PUT ON ICE IMMEDIATELY\n'
                            'Start centrifugation within 2 hours',
                'samples': [
                    {
                        'id_prefix': 'BavSa',
                        'name': '2.7ml EDTA',
                        'count': 1,
                        'print_on_bag': True,
                    },
                    {
                        'id_prefix': 'BavSa',
                        'name': '7.5ml EDTA',
                        'count': 2,
                        'print_on_bag': True,
                    },
                    {
                        'id_prefix': 'BavFm',
                        'name': '',
                        'count': 1,
                        'duplicates': 1,
                        'print_on_bag': False,
                    },
                ],
            },
        ],
    },
    {
        'name': 'Brave Poland Pack',
        'study':  StudyName.BRAVE,
        'participant_id_prefix': 'BavPl',
        'printer_set_name': 'CV BRU2',
        'disable_batch_printing': False,
        'print_recruited_notice': False,
        'participant_label_count': 0,
        'visits': ['Poland'],
        'bags': [
            # {
            #     'title': 'TOREBKA Z SUROWICA I PROBKA EDTA',
            #     'small_format': False,
            #     'subheaders':   '* POBIERZ PROBKE NA SUROWICE (PIERWSZA W KOLEJNOSCI)\n'
            #                     '* UMIESC W TOREBCE\n'
            #                     '* POBNIERZ PROBKE NA EDTA (PIATA W KOLEJNOSCIE)\n'
            #                     '* UMIESC W TOREBCE\n'
            #                     '* NIE UMIESZCZAJ NA LODZIE (TRZYMAJ W TEMPERATURZE POKOJOWEJ)',
            #     'warnings': 'DOSTARCZ DO LABORATORIUM W PRZECIAGU 90 MINUT',
            #     'form_date_text': 'DATA',
            #     'form_time_text': 'GODZINA POBRANIA',
            #     'form_emergency_text': 'PROBKI',
            #     'form_consent_a_text': 'OSOBA UZYSKUJA ZGODE',
            #     'form_consent_b_text': 'NA UDZIAL W BADANIU',
            #     'samples': [
            #         {
            #             'id_prefix': 'BavSa',
            #             'name': '7.5ml PROBKA NA SUROWICE (BRAZOWA)',
            #             'count': 1,
            #             'print_on_bag': True,
            #         },
            #         {
            #             'id_prefix': 'BavSa',
            #             'name': '2.7ml PROBKA EDTA (FIOLETOWA)',
            #             'count': 1,
            #             'print_on_bag': True,
            #         },
            #         {
            #             'id_prefix': 'BavFm',
            #             'name': '',
            #             'count': 1,
            #             'duplicates': 7,
            #             'print_on_bag': False,
            #         },
            #     ],
            # },
            {
                'title': 'TOREBKA Z PROBKAMI EDTA I CYTRYNIANEM',
                'small_format': False,
                'subheaders':   '* UMIESC WSZYSTKIE 3 PROBKI NA LODZIE NA 2 MINUTY (ZEBY SCHLODZIC)\n'
                                '* POBIERZ ZIELONA PROBKE NA KRZEPNIEZIE (DRUGA W KOLEJNOSCI)\n'
                                '* POBIERZ 2 PROBKI NA EDTA (CZERWONE, TRZECIA I CZWARTA W KOLEJNOSCI)\n'
                                '* UMIESC W TOREBCE I UMIESC NA LODZIE\n'
                                '* TRYMAJ NA LODZIE',
                'warnings': 'DOSTARCZ DO LABORATORIUM W PRZECIAGU 90 MINUT',
                'form_date_text': 'DATA',
                'form_time_text': 'GODZINA POBRANIA',
                'form_emergency_text': 'PROBKI',
                'form_consent_a_text': 'OSOBA UZYSKUJA ZGODE',
                'form_consent_b_text': 'NA UDZIAL W BADANIU',
                'font_differential': -2,
                'samples': [
                    {
                        'id_prefix': 'BavSa',
                        'name': '4.3ml PROBKA NA KRZEPNIECIE Z CYTRYNIANEM (ZIELONA)',
                        'count': 1,
                        'print_on_bag': True,
                    },
                    {
                        'id_prefix': 'BavSa',
                        'name': '7.5ml PROBKA EDTA (CZEROWNA)',
                        'count': 2,
                        'print_on_bag': True,
                    },
                ],
            },
        ],
    },
]
def _create_label_bundles():
    for lb in _label_bundles:
        if LabelBundle.query.filter_by(name=lb['name']).one_or_none():
            continue

        bundle = LabelBundle(
            name=lb['name'],
            study=Study.query.filter_by(name=lb['study']['name']).one(),
            participant_id_provider=IdProvider.query.filter_by(prefix=lb['participant_id_prefix']).one_or_none(),
            label_printer_set=LabelPrinterSet.query.filter_by(name=lb['printer_set_name']).one_or_none(),
            disable_batch_printing=lb['disable_batch_printing'],
            print_recruited_notice=lb['print_recruited_notice'],
            participant_label_count=lb['participant_label_count'],
        )

        visits = lb['visits'] or []

        if len(visits) == 0:
            visits.append('')

        for b in lb['bags']:
            for v in visits:
                bag = SampleBagLabel(
                    label_bundle = bundle,
                    title=b['title'],
                    visit=v,
                    subheaders=b['subheaders'],
                    warnings=b['warnings'],
                    small_format=b['small_format'],
                    font_differential=b.get('font_differential', 0),
                    form_date_text=b.get('form_date_text', None),
                    form_time_text=b.get('form_time_text', None),
                    form_emergency_text=b.get('form_emergency_text', None),
                    form_consent_a_text=b.get('form_consent_a_text', None),
                    form_consent_b_text=b.get('form_consent_b_text', None),
                )

                db.session.add(bag)

                for s in b['samples']:
                    db.session.add(SampleLabel(
                        sample_bag_label=bag,
                        id_provider=IdProvider.query.filter_by(prefix=s['id_prefix']).one_or_none(),
                        name=s['name'],
                        count=s['count'],
                        duplicates=s.get('duplicates', 1),
                        print_on_bag=s['print_on_bag'],
                    ))

        db.session.add(bundle)
    
    db.session.commit()
