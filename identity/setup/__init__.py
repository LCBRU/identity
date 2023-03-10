from lbrc_flask.database import db
from identity.model.id import IdProvider, ParticipantIdentifierType
from lbrc_flask.security import get_system_user, get_admin_user
from flask import current_app
from lbrc_flask.python_helpers import get_concrete_classes
from identity.printing import LabelBundle, LabelPrinter, LabelPrinterSet, SampleBagLabel, SampleLabel, AliquotBatch, AliquotLabel, MedicalNotesLabel
from identity.printing import PRINTER_BRU_CRF_BAG, PRINTER_BRU_CRF_SAMPLE, PRINTER_CVRC_LAB_SAMPLE, PRINTER_DEV, PRINTER_LIMB, PRINTER_TMF_BAG, PRINTER_TMF_SAMPLE
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
        'participant_id_name': 'ALLEVIATE Participants',
        'printer_set_name': 'CV TMF',
        'participant_label_count': 35,
        'bags': [
            {
                'title': 'ALLEVIATE (room temp)',
                'visits': ['Baseline', '12 Weeks'],
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'ALLEVIATE Samples',
                        'name': '4.9ml Serum (brown)',
                    },
                    {
                        'id_name': 'ALLEVIATE Samples',
                        'name': '2.7ml EDTA (purple)',
                    },
                ],
            },
            {
                'title': 'ALLEVIATE (on ice)',
                'visits': ['Baseline', '12 Weeks'],
                'warnings': 'Put on ice\nTransfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'ALLEVIATE Samples',
                        'name': '4.9ml Litium Hep. (orange)',
                        'count': 2,
                    },
                    {
                        'id_name': 'ALLEVIATE Samples',
                        'name': '4.9ml EDTA (pink)',
                    },
                ],
            },
        ],
    },
    {
        'name': 'Bioresource Pack',
        'study':  StudyName.Bioresource,
        'participant_id_name': 'Bioresource Participants',
        'printer_set_name': 'CV BRU2',
        'participant_label_count': 1,
    },
    {
        'name': 'Brave Pack',
        'study':  StudyName.BRAVE,
        'participant_id_name': 'BRAVE Participants',
        'printer_set_name': 'CV BRU2',
        'bags': [
            {
                'title': 'Citrate and EDTA Bag',
                'subheaders':   '* Fill citrate bottle 2nd\n'
                                '* Fill EDTA bottles 3rd and 4th\n'
                                '* Put citrate and EDTA on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'BRAVE Samples',
                        'name': '4.3ml Citrate',
                    },
                    {
                        'id_name': 'BRAVE Samples',
                        'name': '7.5ml EDTA',
                        'count': 2,
                    },
                    {
                        'id_name': 'BRAVE Families',
                        'print_on_bag': False,
                        'duplicates': 7,
                    },
                ],
            },
            {
                'title': 'Serum and EDTA Bag',
                'subheaders':   '* Fill serum bottle 1st\n'
                                '* Return to bag\n'
                                '* Fill the 2.7ml EDTA bottle 5th\n'
                                '* Return to bag',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'BRAVE Samples',
                        'name': '2.7ml EDTA',
                    },
                    {
                        'id_name': 'BRAVE Samples',
                        'name': '7.5ml Serum',
                    },
                ],
            },
        ],
    },
    {
        'name': 'Brave External Pack',
        'study':  StudyName.BRAVE,
        'participant_id_name': 'BRAVE External Participants',
        'sidebar_prefix': 'External',
        'printer_set_name': 'CV BRU2',
        'bags': [
            {
                'title': 'EDTA Bag',
                'warnings': 'PUT ON ICE IMMEDIATELY\n'
                            'Start centrifugation within 2 hours',
                'samples': [
                    {
                        'id_name': 'BRAVE Samples',
                        'name': '2.7ml EDTA',
                    },
                    {
                        'id_name': 'BRAVE Samples',
                        'name': '7.5ml EDTA',
                        'count': 2,
                        'print_on_bag': True,
                    },
                    {
                        'id_name': 'BRAVE Families',
                        'print_on_bag': False,
                        'duplicates': 7,
                    },
                ],
            },
        ],
    },
    {
        'name': 'Brave Poland Pack',
        'study':  StudyName.BRAVE,
        'participant_id_name': 'BRAVE Poland Participants',
        'sidebar_prefix': 'Poland',
        'printer_set_name': 'CV BRU2',
        'bags': [
            {
                'title': 'TOREBKA Z SUROWICA I PROBKA EDTA',
                'subheaders':   '* POBIERZ PROBKE NA SUROWICE (PIERWSZA W KOLEJNOSCI)\n'
                                '* UMIESC W TOREBCE\n'
                                '* POBNIERZ PROBKE NA EDTA (PIATA W KOLEJNOSCIE)\n'
                                '* UMIESC W TOREBCE\n'
                                '* NIE UMIESZCZAJ NA LODZIE (TRZYMAJ W TEMPERATURZE POKOJOWEJ)',
                'warnings': 'DOSTARCZ DO LABORATORIUM W PRZECIAGU 90 MINUT',
                'form_date_text': 'DATA',
                'form_time_text': 'GODZINA POBRANIA',
                'form_emergency_text': 'PROBKI',
                'form_consent_a_text': 'OSOBA UZYSKUJA ZGODE',
                'form_consent_b_text': 'NA UDZIAL W BADANIU',
                'font_differential': -2,
                'samples': [
                    {
                        'id_name': 'BRAVE Samples',
                        'name': '7.5ml PROBKA NA SUROWICE (BRAZOWA)',
                    },
                    {
                        'id_name': 'BRAVE Samples',
                        'name': '2.7ml PROBKA EDTA (FIOLETOWA)',
                    },
                    {
                        'id_name': 'BRAVE Families',
                        'duplicates': 7,
                        'print_on_bag': False,
                    },
                ],
            },
            {
                'title': 'TOREBKA Z PROBKAMI EDTA I CYTRYNIANEM',
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
                        'id_name': 'BRAVE Samples',
                        'name': '4.3ml PROBKA NA KRZEPNIECIE Z CYTRYNIANEM (ZIELONA)',
                    },
                    {
                        'id_name': 'BRAVE Samples',
                        'name': '7.5ml PROBKA EDTA (CZEROWNA)',
                        'count': 2,
                    },
                ],
            },
        ],
    },
    {
        'name': 'BRICCS Pack',
        'study':  StudyName.BRICCS,
        'participant_id_name': 'BRICCS Participant Number',
        'printer_set_name': 'CV BRU2',
        'bags': [
            {
                'title': 'Citrate and EDTA Bag',
                'subheaders':   '* Fill citrate bottle 2nd\n'
                                '* Fill EDTA bottles 3rd and 4th\n'
                                '* Put citrate and EDTA on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '4.3ml Citrate',
                    },
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '7.5ml EDTA',
                        'count': 2,
                    },
                    {
                        'id_name': 'BRICCS Sample Number',
                        'count': 2,
                        'print_on_bag': False,
                    },
                ],
            },
            {
                'title': 'Serum and EDTA Bag',
                'subheaders':   '* Fill serum bottle 1st\n'
                                '* Return to bag\n'
                                '* Fill the 2.7ml EDTA bottle 5th\n'
                                '* Return to bag',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '2.7ml EDTA',
                    },
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '7.5ml Serum',
                    },
                ],
            },
            {
                'title': 'Urine Bag',
                'subheaders':   '* Fill with 25ml MSU/CSU\n'
                                '* Put on ice for 2 minutes then\n'
                                '* Return to bag then put back on ice',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '25ml Plain EDTA',
                    },
                ],
            },
        ],
    },
    {
        'name': 'BRICCS Kettering Pack',
        'study':  StudyName.BRICCS,
        'participant_id_name': 'BRICCS Participant Number',
        'printer_set_name': 'CV BRU2',
        'bags': [
            {
                'title': 'EDTA Bag',
                'subheaders':   '* Fill citrate bottle 2nd\n'
                                '* Fill EDTA bottles 3rd and 4th\n'
                                '* Put citrate and EDTA on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'PUT ON ICE IMMEDIATELY\n'
                            'Start centrifugation within 2 hours',
                'samples': [
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '2.7ml EDTA',
                    },
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '7.5ml EDTA',
                        'count': 2,
                    },
                ],
            },
        ],
        'aliquot_batches': [
            {
                'id_name': 'KETTERING BRICCS ALIQUOT',
                'aliquots': [
                    {
                        'prefix': 'p91',
                        'count': 8
                    },
                    {
                        'prefix': 'b91',
                        'count': 1
                    }
                ]
            }
        ]
    },
    {
        'name': 'BRICCS Sample Pack',
        'study':  StudyName.BRICCS,
        'participant_id_name': 'BRICCS Participant Number',
        'printer_set_name': 'CV BRU2',
        'bags': [
            {
                'do_not_print_bag': True,
                'samples': [
                    {
                        'id_name': 'BRICCS Sample Number',
                        'print_on_bag': False,
                    },
                ],
            },
        ],
    },
    {
        'name': 'CAE Pack',
        'study':  StudyName.CAE,
        'participant_id_name': 'CAE Participants',
        'printer_set_name': 'CV BRU2',
        'medical_notes_label': {
            'study_name_line_1': 'Causes of Acute Coronary Syndrome',
            'study_name_line_2': 'in People with SCAD or CAE',
            'chief_investigator': 'Dave Adlam',
            'chief_investigator_email': 'da134@le.ac.uk / dave.adlam@uhl-tr.nhs.uk',
            'study_sponsor': 'University of Leicester',
            'iras_id': '182079',
        },
        'bags': [
            {
                'title': 'Serum and EDTA Bag',
                'subheaders':   '* Fill brown 7.5ml serum bottle 1st\n'
                                '* KEEP AT ROOM TEMPERATURE\n'
                                '* Fill red 7.5ml EDTA bottle 2nd\n'
                                '* PUT ON ICE\n'
                                '* Fill purple 2.7ml EDTA bottle 3rd\n'
                                '* KEEP AT ROOM TEMPERATURE',
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'CAE Samples',
                        'name': '7.5ml Serum',
                    },
                    {
                        'id_name': 'CAE Samples',
                        'name': '7.5ml EDTA',
                    },
                    {
                        'id_name': 'CAE Samples',
                        'name': '2.7ml EDTA',
                    },
                ],
            },
        ],
    },
    {
        'name': 'Cardiomet Pack',
        'study':  StudyName.CARDIOMET,
        'participant_id_name': 'CARDIOMET Participants',
        'printer_set_name': 'CV BRU2',
        'participant_label_count': 8,
        'bags': [
            {
                'title': 'Serum and EDTA Bag',
                'visits': ['V1 Aortic Rest', 'V1 Aortic Stress', 'V1 CS Stress'],
                'font_differential': -1,
                'subheaders':   'Serum: CVS Labs biobanking - process and freeze\n'
                                'EDTA: Gently invert. Place on ice. 5x centrifuge within 20 mins',
                'samples': [
                    {
                        'id_name': 'CARDIOMET Samples',
                        'name': '4.9ml Serum Gel [BROWN]',
                        'count': 2,
                    },
                    {
                        'id_name': 'CARDIOMET Samples',
                        'name': '9ml EDTA [ORANGE/RED]',
                    },
                ],
            },
            {
                'title': 'Serum and EDTA Bag',
                'visits': ['V1 CS Rest', 'V2'],
                'font_differential': -1,
                'subheaders':   'Serum: CVS Labs biobanking - process and freeze\n'
                                'EDTA: Gently invert. Place on ice. 5x centrifuge within 20 mins',
                'samples': [
                    {
                        'id_name': 'CARDIOMET Samples',
                        'name': '4.9ml Serum Gel [BROWN]',
                        'count': 2,
                    },
                    {
                        'id_name': 'CARDIOMET Samples',
                        'name': '9ml EDTA [ORANGE/RED]',
                    },
                    {
                        'id_name': 'CARDIOMET Samples',
                        'name': '2.7ml [EDTA - PURPLE]',
                    },
                ],
            },
        ],
    },
    {
        'name': 'CIA Pack',
        'study':  StudyName.CIA,
        'participant_id_name': 'CIA Participants',
        'printer_set_name': 'CV BRU2',
        'participant_label_count': 5,
        'bags': [
            {
                'title': 'CIA EDTA Bag',
                'samples': [
                    {
                        'id_name': 'CIA Samples',
                        'name': '9.8ml EDTA tube',
                    },
                ],
            },
            {
                'title': 'CIA Serum Bag',
                'samples': [
                    {
                        'id_name': 'CIA Samples',
                        'name': '9.8ml Serum tube',
                    },
                ],
            },
        ],
    },
    {
        'name': 'CMR vs CT-FFR Pack',
        'study':  StudyName.CMR_vs_CTFFR,
        'participant_id_name': 'CMR vs CT-FFR Participants',
        'printer_set_name': 'CV TMF',
        'participant_label_count': 4,
        'medical_notes_label': {
            'study_name_line_1': 'CMR vs CT-FFR in CAD',
            'chief_investigator': 'Dr Jayanth R Arnold',
            'chief_investigator_email': 'jra14@leicester.ac.uk',
            'study_sponsor': 'University of Leicester',
            'iras_id': '258996',
        },
        'bags': [
            {
                'title': 'CMR vs CT-FFR EDTA Bag',
                'subheaders':   '* Put on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'STORE ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'CMR vs CT-FFR Samples',
                        'name': '4.9ml EDTA (pink)',
                    },
                ],
            },
            {
                'title': 'CMR vs CT-FFR Serum Bag',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'CMR vs CT-FFR Samples',
                        'name': '4.9ml Serum (brown)',
                    },
                ],
            },
        ],
    },
    {
        'name': 'COSMIC Pack',
        'study':  StudyName.COSMIC,
        'participant_id_name': 'COSMIC Participants',
        'printer_set_name': 'CV TMF',
        'participant_label_count': 6,
        'bags': [
            {
                'title': 'COSMIC Samples 1',
                'warnings': 'STORE ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'COSMIC Samples',
                        'name': '9ml EDTA (pink)',
                    },
                    {
                        'id_name': 'COSMIC Samples',
                        'name': '4.3ml Citrate (green)',
                    },
                ],
            },
            {
                'title': 'COSMIC Samples 2',
                'warnings': 'ROOM TEMPERATURE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'COSMIC Samples',
                        'name': '9ml Serum (gold)',
                    },
                ],
            },
        ],
    },
    {
        'name': 'Discordance Pack',
        'study':  StudyName.DISCORDANCE,
        'participant_id_name': 'DISCORDANCE Participants',
        'printer_set_name': 'CV TMF',
        'participant_label_count': 6,
    },
    {
        'name': 'ELASTIC-AS Pack',
        'study':  StudyName.ELASTIC_AS,
        'participant_id_name': 'ELASTIC-AS Participants',
        'printer_set_name': 'CV TMF',
        'print_recruited_notice': True,
        'bags': [
            {
                'title': 'ELASTIC-AS EDTA Bag',
                'visits': ['Visit Baseline', 'Visit Month 12'],
                'subheaders':   '* Put EDTA on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'ELASTIC-AS Samples',
                        'name': '9.8ml EDTA (pink)',
                    },
                ],
            },
            {
                'title': 'ELASTIC-AS Serum Bag',
                'visits': ['Visit Baseline', 'Visit Month 12'],
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'ELASTIC-AS Samples',
                        'name': '4.9ml Serum (brown)',
                        'count': 2,
                    },
                    {
                        'id_name': 'ELASTIC-AS Samples',
                        'name': '2.7ml Whole Blood (purple)',
                    },
                ],
            },
        ],
    },
    {
        'name': 'FAST Pack',
        'study':  StudyName.FAST,
        'participant_id_name': 'FAST Participants',
        'printer_set_name': 'CV BRU2',
        'participant_label_count': 6,
    },
    {
        'name': 'GO DCM Pack',
        'study':  StudyName.GO_DCM,
        'participant_id_name': 'GO-DCM Participants',
        'printer_set_name': 'CV TMF',
        'user_defined_participant_id': True,
        'disable_batch_printing': True,
        'participant_label_count': 5,
        'medical_notes_label': {
            'study_name_line_1': 'Go DCM: Defining the genetics, biomarkers',
            'study_name_line_2': 'and outcomes for dilated cardiomyopathy',
            'chief_investigator': 'Dr James Ware',
            'chief_investigator_email': 'j.ware@imperial.ac.uk',
            'study_sponsor': 'NIHR CRN: North West London',
            'iras_id': '237880',
        },
        'bags': [
            {
                'title': 'GO-DCM Substudy EDTA 2 Bag',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'GO-DCM Samples',
                        'name': '2.7ml EDTA',
                    },
                ],
            },
            {
                'title': 'GO-DCM Substudy EDTA Bag',
                'subheaders':   '* Put on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'GO-DCM Samples',
                        'name': '7.9ml EDTA',
                    },
                ],
            },
            {
                'title': 'GO-DCM Baseline Serum Bag',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'GO-DCM Samples',
                        'name': '4.9ml Serum',
                    },
                ],
            },
            {
                'title': 'GO-DCM Baseline EDTA Bag',
                'subheaders':   '* Put on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'GO-DCM Samples',
                        'name': '4.9ml Li Hep Plasma',
                    },
                    {
                        'id_name': 'GO-DCM Samples',
                        'name': '10ml EDTA',
                    },
                ],
            },
        ],
    },
    {
        'name': 'Indapamide Pack',
        'study':  StudyName.Indapamide,
        'participant_id_name': 'Indapamide Participants',
        'printer_set_name': 'CV BRU2',
        'participant_label_count': 4,
        'bags': [
            {
                'title': 'Indapamide EDTA Bag',
                'visits': ['Baseline', '2 Weeks', '6 Weeks', '10 Weeks'],
                'warnings': 'PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'Indapamide Samples',
                        'name': '7.5ml EDTA',
                        'count': 2,
                    },
                ],
            },
            {
                'title': 'Indapamide Serum Bag',
                'visits': ['Baseline', '2 Weeks', '6 Weeks', '10 Weeks'],
                'subheadings': 'Fill Serum bottles 1st & 2nd',
                'warnings': 'KEEP AT ROOM TEMPERATURE',
                'samples': [
                    {
                        'id_name': 'Indapamide Samples',
                        'name': '4.9ml Serum',
                        'count': 2,
                    },
                ],
            },
            {
                'title': 'Indapamide Urine Bag',
                'visits': ['Baseline', '2 Weeks', '6 Weeks', '10 Weeks'],
                'warnings': 'PUT ON ICE',
                'samples': [
                    {
                        'id_name': 'Indapamide Samples',
                        'name': '50ml Urine',
                        'count': 1,
                    },
                ],
            },
        ],
    },
    {
        'name': 'LENTEN Pack',
        'study':  StudyName.LENTEN,
        'participant_id_name': 'LENTEN Participants',
        'printer_set_name': 'CV BRU2',
        'participant_label_count': 8,
        'print_recruited_notice': True,
        'bags': [
            {
                'title': 'LENTEN EDTA Bag',
                'visits': ['Visit 1', 'Visit 2', 'Visit 3', 'Visit 4', 'Visit 5', 'Visit 6'],
                'samples': [
                    {
                        'id_name': 'LENTEN Samples',
                        'name': '7.5ml EDTA',
                        'count': 2,
                    },
                    {
                        'id_name': 'LENTEN Samples',
                        'name': 'Urine',
                        'count': 1,
                        'print_on_bag': False,
                    },
                ],
            },
        ],
    },
    {
        'name': 'LIMb Pack',
        'study':  StudyName.LIMb,
        'participant_id_name': 'LIMb Participants',
        'printer_set_name': 'CV LIMB',
        'participant_label_count': 30,
        'print_recruited_notice': True,
        'bags': [
            {
                'title': 'LIMb EDTA Bag',
                'small_format': True,
                'samples': [
                    {
                        'id_name': 'LIMb Samples',
                        'name': '9ml EDTA on Ice',
                        'duplicates': 2,
                        'duplicate_names': '(Sample)\n(Study Pack)'
                    },
                ],
            },
            {
                'title': 'LIMb Serum Bag',
                'small_format': True,
                'samples': [
                    {
                        'id_name': 'LIMb Samples',
                        'name': '7.5ml Serum on Ice',
                        'duplicates': 2,
                        'duplicate_names': '(Sample)\n(Study Pack)'
                    },
                ],
            },
        ],
    },
    {
        'name': 'MERMAID Pack',
        'study':  StudyName.MERMAID,
        'participant_id_name': 'BRICCS Participant Number',
        'printer_set_name': 'CV BRU2',
        'participant_label_count': 2,
        'bags': [
            {
                'title': 'Citrate and EDTA Bag',
                'subheaders':   '* Fill citrate bottle 2nd\n'
                                '* Fill EDTA bottles 3rd and 4th\n'
                                '* Put citrate and EDTA on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '4.3ml Citrate',
                    },
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '7.5ml EDTA',
                        'count': 2,
                    },
                    {
                        'id_name': 'BRICCS Sample Number',
                        'count': 2,
                        'print_on_bag': False,
                    },
                ],
            },
            {
                'title': 'Serum and EDTA Bag',
                'subheaders':   '* Fill serum bottle 1st\n'
                                '* Return to bag\n'
                                '* Fill the 2.7ml EDTA bottle 5th\n'
                                '* Return to bag',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '2.7ml EDTA',
                    },
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '7.5ml Serum',
                    },
                ],
            },
            {
                'title': 'Urine Bag',
                'subheaders':   '* Fill with 25ml MSU/CSU\n'
                                '* Put on ice for 2 minutes then\n'
                                '* Return to bag then put back on ice',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'BRICCS Sample Number',
                        'name': '25ml Plain EDTA',
                    },
                ],
            },
        ],
    },
    {
        'name': 'Predict Pack',
        'study':  StudyName.PREDICT,
        'participant_id_name': 'PREDICT Participants',
        'printer_set_name': 'CV TMF',
        'participant_label_count': 10,
        'bags': [
            {
                'title': 'PREDICT Samples',
                'warnings':'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'PREDICT Samples',
                        'name': '4.9ml Serum',
                    },
                    {
                        'id_name': 'PREDICT Samples',
                        'name': '2.7ml EDTA',
                    },
                ],
            },
            {
                'title': 'PREDICT Samples',
                'warnings': 'STORE ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'PREDICT Samples',
                        'name': '4.9ml Litium Hep.',
                        'count': 2,
                    },
                    {
                        'id_name': 'PREDICT Samples',
                        'name': '4.9ml EDTA',
                    },
                ],
            },
        ],
    },
    {
        'name': 'Preeclampsia Pack',
        'study':  StudyName.Pre_Eclampsia,
        'participant_id_name': 'PRE-ECLAMPSIA Participants',
        'printer_set_name': 'CV TMF',
        'bags': [
            {
                'title': 'EDTA Bag',
                'subheaders':   'Fill EDTA bottles 2nd, 3rd AND 4th\n'
                                'EDTA on ice for 2 minutes\n'
                                'Return to bag then back on ice',
                'warnings':'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'PRE-ECLAMPSIA Samples',
                        'name': '7.5ml EDTA',
                        'count': 3,
                    },
                ],
            },
            {
                'title': 'Serum & EDTA Bag',
                'subheaders':   'FILL Serum bottles 2nd, 3rd AND 4th\n'
                                'EDTA on ice for 2 minutes\n'
                                'Return to bag then back on ice',
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'PRE-ECLAMPSIA Samples',
                        'name': '7.5ml Serum',
                    },
                    {
                        'id_name': 'PRE-ECLAMPSIA Samples',
                        'name': '2.7ml EDTA',
                    },
                ],
            },
        ],
    },
    {
        'name': 'SCAD Pack',
        'study':  StudyName.SCAD,
        'participant_id_name': 'SCAD Participants',
        'printer_set_name': 'CV BRU2',
        'medical_notes_label': {
            'study_name_line_1': 'Epidemiology, management, outcomes',
            'study_name_line_2': 'and pathophysiology of SCAD',
            'chief_investigator': 'Dave Adlam',
            'chief_investigator_email': 'da134@le.ac.uk / dave.adlam@uhl-tr.nhs.uk',
            'study_sponsor': 'University of Leicester',
            'iras_id': '18234',
        },
        'bags': [
            {
                'title': 'Citrate and EDTA Bag',
                'subheaders':   '* Fill citrate bottle 2nd\n'
                                '* Fill EDTA bottles 3rd and 4th\n'
                                '* Put citrate and EDTA on ice for 2 minutes\n'
                                '* Return to bag then put back on ice',
                'warnings': 'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'SCAD Samples',
                        'name': '4.3ml Citrate',
                    },
                    {
                        'id_name': 'SCAD Samples',
                        'name': '7.5ml EDTA',
                        'count': 2,
                    },
                    {
                        'id_name': 'SCAD Samples',
                        'count': 2,
                        'print_on_bag': False,
                    },
                ],
            },
            {
                'title': 'Serum and EDTA Bag',
                'subheaders':   '* Fill serum bottle 1st\n'
                                '* Return to bag\n'
                                '* Fill the 2.7ml EDTA bottle 5th\n'
                                '* Return to bag',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'SCAD Samples',
                        'name': '2.7ml EDTA',
                    },
                    {
                        'id_name': 'SCAD Samples',
                        'name': '7.5ml Serum',
                    },
                ],
            },
            {
                'title': 'Urine Bag',
                'subheaders':   '* Fill with 25ml MSU/CSU\n'
                                '* Put on ice for 2 minutes then\n'
                                '* Return to bag then put back on ice',
                'warnings': 'DO NOT PUT ON ICE\n'
                            'Transfer to lab within 90 minutes',
                'samples': [
                    {
                        'id_name': 'SCAD Samples',
                        'name': '25ml Plain EDTA',
                    },
                ],
            },
        ],
    },
    {
        'name': 'SCAD Blood Only Pack',
        'study':  StudyName.SCAD,
        'participant_id_name': 'SCAD Participants',
        'printer_set_name': 'CV BRU2',
        'participant_label_count': 1,
        'bags': [
            {
                'do_not_print_bag': True,
                'samples': [
                    {
                        'id_name': 'SCAD Samples',
                        'print_on_bag': False,
                        'count': 3,
                    },
                ],
            },
        ],
    },
    {
        'name': 'SCAD Family Pack',
        'study':  StudyName.SCAD,
        'participant_id_name': 'SCAD Participants',
        'printer_set_name': 'CV BRU2',
        'bags': [
            {
                'do_not_print_bag': True,
                'samples': [
                    {
                        'id_name': 'SCAD Families',
                        'print_on_bag': False,
                        'count': 7,
                    },
                ],
            },
        ],
    },
    {
        'name': 'SCAD Registry Pack',
        'study':  StudyName.SCAD,
        'participant_id_name': 'SCAD Participants',
        'printer_set_name': 'CV BRU2',
        'bags': [
            {
                'do_not_print_bag': True,
                'samples': [
                    {
                        'id_name': 'SCAD REG IDS',
                        'print_on_bag': False,
                    },
                ],
            },
        ],
    },
    {
        'name': 'SPIRAL Pack',
        'study':  StudyName.SPIRAL,
        'participant_id_name': 'SPIRAL Participants',
        'printer_set_name': 'CV Lab',
        'participant_label_count': 5,
    },
]
def _create_label_bundles():
    for lb in _label_bundles:
        if LabelBundle.query.filter_by(name=lb['name']).one_or_none():
            continue

        bundle = LabelBundle(
            name=lb['name'],
            study=Study.query.filter_by(name=lb['study']['name']).one(),
            sidebar_prefix=lb.get('sidebar_prefix', ''),
            participant_id_provider=IdProvider.query.filter_by(name=lb.get('participant_id_name', '')).one_or_none(),
            label_printer_set=LabelPrinterSet.query.filter_by(name=lb.get('printer_set_name', '')).one_or_none(),
            disable_batch_printing=lb.get('disable_batch_printing', False),
            print_recruited_notice=lb.get('print_recruited_notice', False),
            participant_label_count=lb.get('participant_label_count', 0),
            user_defined_participant_id=lb.get('user_defined_participant_id', False),
        )

        if mnl := lb.get('medical_notes_label', None):
            db.session.add(MedicalNotesLabel(
                label_bundle=bundle,
                study_name_line_1=mnl.get('study_name_line_1', ''),
                study_name_line_2=mnl.get('study_name_line_2', ''),
                chief_investigator=mnl.get('chief_investigator', ''),
                chief_investigator_email=mnl.get('chief_investigator_email', ''),
                study_sponsor=mnl.get('study_sponsor', ''),
                iras_id=mnl.get('iras_id', ''),
            ))

        for b in lb.get('bags', []):
            for v in b.get('visits', ['']):
                bag = SampleBagLabel(
                    label_bundle=bundle,
                    title=b.get('title', ''),
                    visit=v,
                    subheaders=b.get('subheaders', ''),
                    warnings=b.get('warnings', ''),
                    small_format=b.get('small_format', False),
                    do_not_print_bag=b.get('do_not_print_bag', False),
                    font_differential=b.get('font_differential', 0),
                    form_date_text=b.get('form_date_text', None),
                    form_time_text=b.get('form_time_text', None),
                    form_emergency_text=b.get('form_emergency_text', None),
                    form_consent_a_text=b.get('form_consent_a_text', None),
                    form_consent_b_text=b.get('form_consent_b_text', None),
                )

                db.session.add(bag)

                for s in b.get('samples', []):
                    db.session.add(SampleLabel(
                        sample_bag_label=bag,
                        id_provider=IdProvider.query.filter_by(name=s['id_name']).one_or_none(),
                        name=s.get('name', ''),
                        count=s.get('count', 1),
                        duplicates=s.get('duplicates', 1),
                        duplicate_names=s.get('duplicate_names', None),
                        print_on_bag=s.get('print_on_bag', True),
                    ))
            
        for ab in lb.get('aliquot_batches', []):
            a_batch = AliquotBatch(
                label_bundle=bundle,
                id_provider=IdProvider.query.filter_by(name=ab['id_name']).one_or_none(),
            )
            db.session.add(a_batch)

            for a in ab.get('aliquots', []):
                db.session.add(AliquotLabel(
                    aliquot_batch=a_batch,
                    prefix=a.get('prefix', ''),
                    count=a.get('count', 1),
                ))

        db.session.add(bundle)
    
    db.session.commit()
