#!/usr/bin/env python3

from itertools import cycle
from random import randint
from dotenv import load_dotenv
from lbrc_flask.database import db
from lbrc_flask.security import init_roles, init_users
from identity.model import Study
from identity.model.blinding import BlindingType
from identity.model.edge import EdgeSiteStudy
from identity.model.id import PseudoRandomIdProvider
from identity.printing import LabelBundle
from identity.setup import setup_data
from faker import Faker
fake = Faker()


load_dotenv()

from identity import create_app

application = create_app()
application.app_context().push()
db.create_all()
init_roles([])
init_users()

setup_data()


# Edge Studies
edge_studies = [EdgeSiteStudy(
    project_id=fake.ean(length=8),
    iras_number=fake.license_plate(),
    project_short_title=fake.word().upper(),
) for _ in range(6)]

db.session.add_all(edge_studies)
db.session.commit()


# Studies
studies = [Study(name=fake.word().upper(), edge_id=es.project_id) for es in edge_studies]

db.session.add_all(studies)
db.session.commit()


# Labels
disable_batch_printing=cycle([True, False])
user_defined_participant_id=cycle([True, False, False])
bundles = []
for s in studies:
    bundles.extend([LabelBundle(
        name=f'{s.name} {i}',
        study_id=s.id,
        disable_batch_printing=next(disable_batch_printing),
        user_defined_participant_id=next(user_defined_participant_id),
    ) for i in range(1, randint(1, 5))])

db.session.add_all(bundles)
db.session.commit()


# Blinding
blinding_types = []
for s in studies:

    blinding_types.extend([BlindingType(
        name=f'{s.name} {i}',
        study_id=s.id,
        pseudo_random_id_provider=PseudoRandomIdProvider(
            name=fake.word().title(),
            prefix=fake.word()[0:3].upper(),
        ),

    ) for i in range(1, randint(1, 5))])

db.session.add_all(blinding_types)
db.session.commit()


db.session.close()
