#!/usr/bin/env python3
from dotenv import load_dotenv

from tests.faker import IdentityProvider

load_dotenv()

from datetime import date, timedelta
from itertools import cycle
from random import randint, choice
from dotenv import load_dotenv
from lbrc_flask.database import db
from lbrc_flask.security import init_roles, init_users
from sqlalchemy import select
from identity.database import civicrm_session
from identity.model import Study
from identity.model.blinding import BlindingType
from identity.model.edge import EdgeSiteStudy
from identity.model.civicrm import (
    CiviCrmStudy,
)
from identity.model.id import PseudoRandomIdProvider
from identity.printing import LabelBundle
from identity.setup import setup_data
from faker import Faker
from alembic.config import Config
from alembic import command
from lbrc_flask.pytest.faker import LbrcFlaskFakerProvider

fake = Faker("en_GB")
fake.add_provider(LbrcFlaskFakerProvider)
fake.add_provider(IdentityProvider)

load_dotenv()

from identity import create_app

application = create_app()
application.app_context().push()
db.create_all()
init_roles([])
init_users()

alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")

setup_data()

study_names = [
    'Amaze',
    'Bioresource',
    'Brave',
    'BRICCS',
    'Cardiomet',
    'Discordance',
    'Dream',
    'EMMACE 4',
    'FAST',
    'FOAMI',
    'GENVASC',
    'Global Leaders',
    'Graphic 2',
    'Indapamide',
    'Interval',
    'Lenten',
    'LIMB',
    'National Bioresource',
    'OMICS',
    'Predict',
    'Preeclampsia',
    'SCAD',
    'SPIRAL',
    'TMAO',
]
primary_clinical_management_areas = cycle([fake.word().title() for _ in range(13)])
status = cycle(['Cancel', 'Loaded', 'Deleted'])
principle_investigator = cycle(fake.name() for _ in range(5))
lead_nurse = cycle(fake.name() for _ in range(5))


fake.civicrm_gender().create_defaults()
genders = fake.civicrm_gender().all_from_db()

fake.civicrm_case_status().create_defaults()
case_statuses = fake.civicrm_case_status().all_from_db()

fake.civicrm_study().create_defaults()
civicrm_studies = fake.civicrm_study().all_from_db()

civicrm_participants = fake.civicrm_participant().get_list(
    save=True,
    item_count=200,
    study=fake.civicrm_study().choice_from_db,
    status=fake.civicrm_case_status().choice_from_db,
)


# Edge Studies
edge_studies = []
for s in study_names:
    start_date = date.today() - timedelta(days=fake.pyint(30, 300))
    study_length = fake.pyint(30, 600)
    end_date = start_date + timedelta(days=study_length)
    if fake.pyint(1, 100) < 75:
        target_recruitment=10*fake.pyint(1, 100)
    else:
        target_recruitment=None

    es = EdgeSiteStudy(
        project_id=fake.ean(length=8),
        iras_number=fake.license_plate(),
        project_short_title=s,
        primary_clinical_management_areas=next(primary_clinical_management_areas),
        project_site_status=next(status),
        principal_investigator=next(principle_investigator),
        project_site_lead_nurses=next(lead_nurse),

        project_site_rand_submission_date=fake.date_object(),
        project_site_start_date_nhs_permission=start_date,
        project_site_date_site_confirmed=start_date + timedelta(days=fake.pyint(-10,10)),
        project_site_planned_closing_date=fake.date_object(),
        project_site_closed_date=fake.date_object(),
        project_site_actual_recruitment_end_date=end_date,
        project_site_planned_recruitment_end_date=end_date + timedelta(days=fake.pyint(-10,10)),
        project_site_target_participants=target_recruitment,
    )

    es.calculate_values()
    es.recruited_org = int(es.target_requirement_by or 0) * choice([0.1,0.5,0.6,0.8,0.85,0.9,0.95,1,1.05,1.10,1.50])
    es.calculate_values()

    edge_studies.append(es)

db.session.add_all(edge_studies)
db.session.commit()


# Studies
with civicrm_session() as sesh:
    civicrm_studies = sesh.execute(select(CiviCrmStudy)).scalars()
    studies = [Study(name=es.project_short_title, edge_id=es.project_id, civicrm_study_id=cs.id) for es, cs in zip(edge_studies, civicrm_studies)]

db.session.add_all(studies)
db.session.commit()

studies = db.session.execute(select(Study)).unique().scalars()

# Labels
disable_batch_printing=cycle([True, False])
user_defined_participant_id=cycle([True, False, False])
bundles = []
for s in studies:
    bundles.extend([LabelBundle(
        name=f'{s.name} {i}',
        study=s,
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
