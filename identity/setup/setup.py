from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.setup.studies import StudyName
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from flask import current_app
from itertools import chain
from collections import ChainMap
from lbrc_flask.database import db
from identity.model.id import (
    SequentialIdProvider,
    LegacyIdProvider,
    LegacyId,
    PseudoRandomIdProvider,
    PseudoRandomId,
    BioresourceIdProvider,
    BioresourceId,
    StudyIdSpecification,
    ParticipantIdentifierType,
)
from lbrc_flask.python_helpers import get_concrete_classes
from identity.model import Study
from identity.ecrfs.model import RedcapInstance
from lbrc_flask.security import get_system_user, get_admin_user
from identity.printing.briccs import (
    ID_NAME_BRICCS_PARTICIPANT,
    ID_NAME_BRICCS_SAMPLE,
)
from identity.printing.model import LabelPack
from identity.blinding import BLINDING_SETS
from identity.blinding.model import (
    BlindingSet,
    BlindingType,
    Blinding,
)
from identity.ecrfs.setup import crfs


PSEUDORANDOM_ID_PROVIDERS = {}


def create_base_data():
    current_app.logger.info('create_base_data')

    system = get_system_user()

    create_providers(system)
    create_studies(system)
    create_label_packs(system)
    create_blinding_sets(system)
    create_participant_id_types(system)
    create_redcap_instances(system)
    create_partipipant_import_definitions(system)


def import_ids():
    current_app.logger.info('import_ids')

    system = get_system_user()

    load_legacy_briccs_ids(system)
    load_legacy_bioresource_ids(system)
    load_legacy_pseudorandom_ids(system)
    load_legacy_blind_ids(system)


def load_legacy_briccs_ids(admin):
    current_app.logger.info('load_legacy_briccs_ids')

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

                current_app.logger.info(f'Creating: {provider.prefix}{id[4:]}')
                legacy_ids.append(LegacyId(
                    legacy_id_provider_id=provider.id,
                    number=number,
                    last_updated_by_user_id=admin.id,
                ))

        engine.dispose()

        db.session.bulk_save_objects(legacy_ids)

    db.session.commit()


def load_legacy_bioresource_ids(admin):
    current_app.logger.info(f'load_legacy_bioresource_ids')

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

                current_app.logger.info(f'Creating: {new_id.full_code}')

                bioresource_ids.append(new_id)

        engine.dispose()

        db.session.bulk_save_objects(bioresource_ids)

    db.session.commit()


def load_legacy_pseudorandom_ids(admin):
    current_app.logger.info(f'load_legacy_pseudorandom_ids')

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

            current_app.logger.info(f'{provider.prefix}: existing = {previous_ordinal}; new = {current_ordinal}')
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

                current_app.logger.info(f'Creating: {row["fullcode"]}')
                pseudo_random_ids.append(new_id)

            db.session.bulk_save_objects(pseudo_random_ids)

        engine.dispose()

    db.session.commit()


def load_legacy_blind_ids(admin):
    current_app.logger.info(f'Loading Blind IDs')

    for bt in BlindingType.query.filter_by(deleted = False).all():
        
        current_app.logger.info(f'Loading Blind IDs of type {bt.name}')

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

                if pseudo_random_id and Blinding.query.filter(Blinding.blinding_type_id == bt.id, Blinding.unblind_id == row['unblind_id']).count() == 0:

                    blinding = Blinding(    
                        unblind_id=row['unblind_id'],
                        blinding_type=bt,
                        blinding_type_id=bt.id,
                        pseudo_random_id=pseudo_random_id,
                        pseudo_random_id_id=pseudo_random_id.id,
                        last_updated_by_user=admin,
                        last_updated_by_user_id=admin.id,
                    )

                    current_app.logger.info(f'Creating Blinding: {blinding}')

                    db.session.add(blinding)

        engine.dispose()

    db.session.commit()


def create_label_packs(user):
    current_app.logger.info(f'Creating Label Packs')

    for x in get_concrete_classes(LabelPack):

        if LabelPack.query.filter_by(type=x.__class__.__name__).count() == 0:
            current_app.logger.info(f'Creating {x.name}')

            x.study = Study.query.filter_by(name=x.__study_name__).first()

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
                last_updated_by_user=user,
            ))

    for prefix, name in ChainMap({}, *chain.from_iterable([x.legacy_identifier_types for x in get_concrete_classes(StudyIdSpecification)])).items():
        if LegacyIdProvider.query.filter_by(name=name).count() == 0:
            current_app.logger.info(f'Creating provider {name}')
            db.session.add(LegacyIdProvider(
                name=name,
                prefix=prefix,
                number_fixed_length=8,
                last_updated_by_user=user,
            ))

    for params in chain.from_iterable([x.sequential_identifier_types for x in get_concrete_classes(StudyIdSpecification)]):
        if SequentialIdProvider.query.filter_by(name=params['name']).count() == 0:
            current_app.logger.info(f'Creating provider {params["name"]}')
            db.session.add(SequentialIdProvider(
                last_updated_by_user=user,
                **params,
            ))

    for prefix, name in ChainMap({}, *chain.from_iterable([x.bioresource_identifier_types for x in get_concrete_classes(StudyIdSpecification)])).items():
        if BioresourceIdProvider.query.filter_by(name=name).count() == 0:
            current_app.logger.info(f'Creating provider {name}')
            db.session.add(BioresourceIdProvider(
                name=name,
                prefix=prefix,
                last_updated_by_user=user,
            ))

    db.session.commit()


def create_studies(user):
    current_app.logger.info(f'Creating Studies')

    for study_name in StudyName().all_studies():
        study = Study.query.filter_by(name=study_name).first()

        if not study:
            current_app.logger.info(f'Creating Study {study_name}')

            study = Study(name=study_name)
            db.session.add(study)

        admin = get_admin_user()
        admin.studies.add(study)
        db.session.add(admin)

    db.session.commit()


def create_blinding_sets(user):
    current_app.logger.info(f'create_blinding_sets')

    for blinding_set_name, bs in BLINDING_SETS.items():

        blinding_set = BlindingSet.query.filter_by(name=blinding_set_name).one_or_none()

        if blinding_set is None:

            current_app.logger.info(f'Creating Blinding Set "{blinding_set_name}"')

            study = Study.query.filter_by(name=bs['study']).first()
            blinding_set = BlindingSet(name=blinding_set_name, study=study)
            db.session.add(blinding_set)

        for type_name, pseudo_random_id_provider_prefix in bs['types'].items():
            pseudo_random_id_provider = PseudoRandomIdProvider.query.filter_by(
                prefix=pseudo_random_id_provider_prefix
            ).first()

            if not pseudo_random_id_provider:
                prid_name='{}: {}'.format(blinding_set_name, type_name)

                current_app.logger.info(f'Creating Pseudorandom ID Provider "{prid_name}"')
        
                pseudo_random_id_provider = PseudoRandomIdProvider(
                    name=prid_name,
                    prefix=pseudo_random_id_provider_prefix,
                    last_updated_by_user=user,
                )
                db.session.add(pseudo_random_id_provider)
                db.session.flush()
            
            current_app.logger.info(f'Creating Blinding Type "{type_name}"')
        
            if BlindingType.query.filter_by(name=type_name, pseudo_random_id_provider=pseudo_random_id_provider).count() == 0:
                blinding_type = BlindingType(
                    name=type_name,
                    blinding_set=blinding_set,
                    pseudo_random_id_provider=pseudo_random_id_provider,
                )

                db.session.add(blinding_type)

    db.session.flush()
    db.session.commit()


def create_participant_id_types(user):
    current_app.logger.info(f'Creating Participant ID Types')

    for name in ParticipantIdentifierTypeName().all_types():
        if ParticipantIdentifierType.query.filter_by(name=name).count() == 0:
            current_app.logger.info(f'Creating Participant ID Type "{name}"')

            db.session.add(ParticipantIdentifierType(
                name=name,
                last_updated_by_user=user,
            ))
    db.session.commit()


def create_redcap_instances(user):
    current_app.logger.info(f'Creating REDCap Instances')

    for i in REDCapInstanceDetail().all_instances():
        if RedcapInstance.query.filter_by(name=i['name']).count() == 0:
            db.session.add(RedcapInstance(**i, last_updated_by_user=user))

    db.session.commit()


def create_partipipant_import_definitions(user):
    current_app.logger.info(f'Creating particpant import definitions')

    for c in crfs:
        db.session.add_all(c.get_partipipant_import_definitions(user))
    
    db.session.commit()