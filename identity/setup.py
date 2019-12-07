#!/usr/bin/env python3

import inspect
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from flask import current_app
from itertools import groupby
from .database import db
from .model import (
    SequentialIdProvider,
    LegacyIdProvider,
    LegacyId,
    PseudoRandomIdProvider,
    PseudoRandomId,
    BioresourceIdProvider,
    BioresourceId,
    Study,
)
from .security import get_system_user, get_admin_user
from .printing.briccs import (
    ID_NAME_BRICCS_PARTICIPANT,
    ID_NAME_BRICCS_SAMPLE,
    ID_NAME_BRICCS_ALIQUOT,
)
from .printing.scad import (
    ID_NAME_SCAD_REG,
    PREFIX_SCAD_REG,
)
from .printing.model import LabelPack
from .blinding import BLINDING_SETS
from .blinding.model import (
    BlindingSet,
    BlindingType,
    Blinding,
)


PSEUDORANDOM_ID_PROVIDERS = {
    'ALLEVIATE Participants': 'AllPt',
    'ALLEVIATE Samples': 'AllSa',
    'BRAVE Participants': 'BavPt',
    'BRAVE Samples': 'BavSa',
    'BRAVE Families': 'BavFm',
    'BRAVE Poland Participants': 'BavPl',
    'BRAVE External Participants': 'BavXPt',
    'CAE Participants': 'CaePt',
    'CAE Samples': 'CaeSa',
    'CARDIOMET Participants': 'CarPt',
    'CARDIOMET Samples': 'CarSa',
    'CIA Participants': 'CiaPt',
    'CIA Samples': 'CiaSa',
    'DISCORDANCE Participants': 'DisPt',
    'ELASTIC-AS Samples': 'EasSa',
    'ELASTIC-AS Participants': 'EasPt',
    'FAST Participants': 'FST',
    'Indapamide Participants': 'IndPt',
    'Indapamide Samples': 'IndSa',
    'LENTEN Participants': 'LenPt',
    'LENTEN Samples': 'LenSa',
    'LIMb Participants': 'LMbPt',
    'LIMb Samples': 'LMbSa',
    'PREDICT Participants': 'PrePt',
    'PREDICT Samples': 'PreSa',
    'PRE-ECLAMPSIA Participants': 'PePt',
    'PRE-ECLAMPSIA Samples': 'PeSa',
    'SCAD Participants': 'ScPt',
    'SCAD Samples': 'ScSa',
    'SCAD Families': 'ScFm',
    'SPIRAL Participants': 'SpPt',
}


def create_base_data():
    print('Creating Base Data')

    system = get_system_user()

    create_providers(system)
    create_studies(system)
    create_label_sets(system)
    create_blinding_sets(system)


def import_ids():
    print('Importing IDs')

    system = get_system_user()

    load_legacy_briccs_ids(system)
    load_legacy_bioresource_ids(system)
    load_legacy_pseudorandom_ids(system)
    load_legacy_blind_ids(system)


def load_legacy_briccs_ids(admin):
    if LegacyId.query.count() == 0:
        briccs_partipants = LegacyIdProvider.query.filter_by(name=ID_NAME_BRICCS_PARTICIPANT).first()
        briccs_samples = LegacyIdProvider.query.filter_by(name=ID_NAME_BRICCS_SAMPLE).first()

        engine = create_engine(current_app.config['LEGACY_BRICCS_ID_URI'])

        with engine.connect() as con:

            rs = con.execute('SELECT id FROM identifiers;')

            legacy_ids = []

            for row in rs:
                id = row['id']
                if id[0:4] == 'PAR_':
                    provider = briccs_partipants
                elif id[0:4] == 'SAM_':
                    provider = briccs_samples
                else:
                    raise Exception('Invalid legacy BRICCS id type: {}'.format(id[0:4]))

                number = int(id[4:])

                print('Creating:', provider.prefix + id[4:])
                legacy_ids.append(LegacyId(
                    legacy_id_provider_id=provider.id,
                    number=number,
                    last_updated_by_user_id=admin.id,
                ))

        engine.dispose()

        db.session.bulk_save_objects(legacy_ids)

    db.session.commit()


def load_legacy_bioresource_ids(admin):
    if BioresourceId.query.count() == 0:
        bioresource_id_provider = BioresourceIdProvider.query.filter_by(prefix='BR').first()

        engine = create_engine(current_app.config['LEGACY_PSEUDORANDOM_ID_URI'])

        with engine.connect() as con:

            rs = con.execute('SELECT nihr_br_id, nihr_br_old_id, check_digit FROM nihr_br_ids;')

            bioresource_ids = []

            for row in rs:
                new_id = BioresourceId(
                    bioresource_id_provider=bioresource_id_provider,
                    bioresource_id_provider_id=bioresource_id_provider.id,
                    number=row['nihr_br_id'],
                    legacy_number=row['nihr_br_old_id'],
                    check_character=row['check_digit'],
                    last_updated_by_user_id=admin.id,
                )

                if not bioresource_id_provider.validate(new_id.full_code):
                    raise Exception('Invalid legacy Bioresource id: {}'.format(new_id.full_code))

                print('Creating:', new_id.full_code)

                bioresource_ids.append(new_id)

        engine.dispose()

        db.session.bulk_save_objects(bioresource_ids)

    db.session.commit()


def load_legacy_pseudorandom_ids(admin):
    print('Loading Pseudi IDs')

    for provider in PseudoRandomIdProvider.query.all():

        previous_ordinal = db.session.query(db.func.max(PseudoRandomId.ordinal)).filter_by(pseudo_random_id_provider_id=provider.id).scalar() or 0

        engine = create_engine(current_app.config['LEGACY_PSEUDORANDOM_ID_URI'])

        with engine.connect() as con:

            current_ordinal = con.execute("""
                SELECT MAX(ordinal)
                FROM unique_ids
                WHERE prefix = %s
                ;""", provider.prefix).scalar()


            rs = con.execute(text("""
                SELECT id, ordinal, prefix, unique_id, check_digit, fullcode
                FROM unique_ids
                WHERE prefix = :prefix
                    AND ordinal > :previous_ordinal
                ;"""), prefix=provider.prefix, previous_ordinal=previous_ordinal)

            print('{}: existing = {}; new = {}'.format(provider.prefix, previous_ordinal, current_ordinal))
            pseudo_random_ids = []

            for row in rs:
                new_id = PseudoRandomId(
                        pseudo_random_id_provider_id=provider.id,
                        ordinal=row['ordinal'],
                        unique_code=row['unique_id'],
                        check_character=row['check_digit'],
                        full_code=row['fullcode'],
                        last_updated_by_user_id=admin.id,
                    )

                if not provider.validate(row['fullcode']):
                    raise Exception('Invalid legacy PseudoRandom ID: {}'.format(row['fullcode']))

                if provider._get_id(row['ordinal']) != row['fullcode']:
                    raise Exception('Legacy PseudoRandom ID (\'{}\') does not match current algorithm (\'{}\')'.format(row['fullcode'], provider._get_id(row['ordinal'])))

                print('Creating:', row['fullcode'])
                pseudo_random_ids.append(new_id)

            db.session.bulk_save_objects(pseudo_random_ids)

        engine.dispose()

    db.session.commit()


def load_legacy_blind_ids(admin):
    print('Loading Blind IDs')

    for bt in BlindingType.query.all():
        
        if len(bt.blindings) == 0:
            print('Loading Blind IDs of type {}'.format(bt.name))

            engine = create_engine(current_app.config['LEGACY_PSEUDORANDOM_ID_URI'])

            with engine.connect() as con:

                rs = con.execute(text("""
                    SELECT unblind_id, blind_id
                    FROM blind_unblind_xref
                    WHERE study = :study
                        AND blind_id_type = :blind_id_type
                    ;"""), study=bt.blinding_set.study.name, blind_id_type=bt.name)

                for row in rs:
                    pseudo_random_id = PseudoRandomId.query.filter_by(full_code=row['blind_id']).first()

                    blinding = Blinding(
                        unblind_id=row['unblind_id'],
                        blinding_type=bt,
                        blinding_type_id=bt.id,
                        pseudo_random_id=pseudo_random_id,
                        pseudo_random_id_id=pseudo_random_id.id,
                        last_updated_by_user=admin,
                        last_updated_by_user_id=admin.id,
                    )

                    print('Creating Blinding:', blinding)

                    db.session.add(blinding)

            engine.dispose()

    db.session.commit()


def create_providers(user):
    print('Creating Providers')

    if LegacyIdProvider.query.filter_by(name=ID_NAME_BRICCS_PARTICIPANT).count() == 0:
        briccs_partipants = LegacyIdProvider(
            name=ID_NAME_BRICCS_PARTICIPANT,
            prefix='BPt',
            number_fixed_length=8,
            last_updated_by_user_id=user.id,
        )
        db.session.add(briccs_partipants)

    if LegacyIdProvider.query.filter_by(name=ID_NAME_BRICCS_SAMPLE).count() == 0:
        briccs_samples = LegacyIdProvider(
            name=ID_NAME_BRICCS_SAMPLE,
            prefix='BSa',
            number_fixed_length=8,
            last_updated_by_user_id=user.id,
        )
        db.session.add(briccs_samples)
    
    if SequentialIdProvider.query.filter_by(name='KETTERING ' + ID_NAME_BRICCS_ALIQUOT).count() == 0:
        db.session.add(SequentialIdProvider(
            name='KETTERING ' + ID_NAME_BRICCS_ALIQUOT,
            last_updated_by_user=user,
            last_number=380,
        ))

    if SequentialIdProvider.query.filter_by(name=ID_NAME_SCAD_REG).count() == 0:
        db.session.add(SequentialIdProvider(
            name=ID_NAME_SCAD_REG,
            prefix=PREFIX_SCAD_REG,
            zero_fill_size=5,
            last_updated_by_user=user,
            last_number=1999,
        ))

    for name, prefix in PSEUDORANDOM_ID_PROVIDERS.items():
        if PseudoRandomIdProvider.query.filter_by(name=name).count() == 0:
            db.session.add(PseudoRandomIdProvider(
                name=name,
                prefix=prefix,
                last_updated_by_user=user,
            ))

    if BioresourceIdProvider.query.filter_by(prefix='BR').count() == 0:
        bioresource_partipants = BioresourceIdProvider(
            name='Bioresource Participants',
            prefix='BR',
            last_updated_by_user_id=user.id,
        )
        db.session.add(bioresource_partipants)

    db.session.commit()


def create_label_sets(user):
    print('Creating Label Sets')

    for x in get_concrete_label_sets():

        if LabelPack.query.filter_by(type=x.__class__.__name__).count() == 0:
            print('Creating ' + x.name)

            x.study = Study.query.filter_by(name=x.__study_name__).first()

            db.session.add(x)

    db.session.commit()


def get_concrete_label_sets(cls=None):

    if (cls is None):
        cls = LabelPack

    result = [sub() for sub in cls.__subclasses__()
              if len(sub.__subclasses__()) == 0 and
              # If the constructor requires parameters
              # other than self (i.e., it has more than 1
              # argument), it's an abstract class
              len(inspect.getfullargspec(sub.__init__)[0]) == 1]

    for sub in [sub for sub in cls.__subclasses__()
                if len(sub.__subclasses__()) != 0]:
        result += get_concrete_label_sets(sub)

    return result


def create_studies(user):
    print('Creating Studies')

    for study_name in set([x.__study_name__ for x in get_concrete_label_sets()]):
        study = Study.query.filter_by(name=study_name).first()

        if not study:
            print('Creating study ' + study_name)

            study = Study(name=study_name)
            db.session.add(study)

        admin = get_admin_user()
        admin.studies.add(study)
        db.session.add(admin)


    db.session.commit()


def create_blinding_sets(user):
    print('Creating Blinding Sets')

    for blinding_set_name, bs in BLINDING_SETS.items():

        if BlindingSet.query.filter_by(name=blinding_set_name).count() == 0:

            print('Creating Blinding Set "{}"'.format(blinding_set_name))

            study = Study.query.filter_by(name=bs['study']).first()
            blinding_set = BlindingSet(name=blinding_set_name, study=study)
            db.session.add(blinding_set)

            for type_name, pseudo_random_id_provider_prefix in bs['types'].items():
                pseudo_random_id_provider = PseudoRandomIdProvider.query.filter_by(
                    prefix=pseudo_random_id_provider_prefix
                ).first()

                if not pseudo_random_id_provider:
                    prid_name='{}: {}'.format(blinding_set_name, type_name)

                    print('Creating Pseudorandom ID Provider "{}"'.format(prid_name))
            
                    pseudo_random_id_provider = PseudoRandomIdProvider(
                        name=prid_name,
                        prefix=pseudo_random_id_provider_prefix,
                        last_updated_by_user=user,
                    )
                    db.session.add(pseudo_random_id_provider)
                
                print('Creating Blinding Type "{}"'.format(type_name))
            
                blinding_type = BlindingType(
                    name=type_name,
                    blinding_set=blinding_set,
                    pseudo_random_id_provider=pseudo_random_id_provider,
                )

                db.session.add(blinding_type)

    db.session.commit()
