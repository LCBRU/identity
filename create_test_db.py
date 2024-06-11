#!/usr/bin/env python3

from itertools import cycle
from random import randint
from dotenv import load_dotenv
from lbrc_flask.database import db
from lbrc_flask.security import init_roles, init_users
from identity.model import Study
from identity.model.blinding import BlindingType
from identity.model.edge import EdgeSiteStudy
from identity.model.civicrm import CiviCrmStudy, CiviCrmParticipant
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

study_names = [fake.word().upper() for _ in range(13)]
primary_clinical_management_areas = cycle([fake.word().title() for _ in range(13)])
status = cycle(['Cancel', 'Loaded', 'Deleted'])
principle_investigator = cycle(fake.name() for _ in range(5))
lead_nurse = cycle(fake.name() for _ in range(5))


# CiviCRM Studies
civicrm_studies = [CiviCrmStudy(
    name=s,
    title=s,
    description=fake.sentence(),
    is_active=True,
) for s in study_names]

db.session.add_all(civicrm_studies)
db.session.commit()


# CiviCRM Participants
civicrm_participants = []

for cs in civicrm_studies:
    civicrm_participants.extend([
        CiviCrmParticipant(
            study_id=cs.id,
            subject=fake.license_plate(),
            start_date=fake.date_object(),
            end_date=fake.date_object(),
            status_id=1,
            is_deleted=False,
    ) for _ in range(randint(15, 25))])

db.session.add_all(civicrm_participants)
db.session.commit()


# Edge Studies
edge_studies = [EdgeSiteStudy(
    project_id=fake.ean(length=8),
    iras_number=fake.license_plate(),
    project_short_title=s,
    primary_clinical_management_areas=next(primary_clinical_management_areas),
    project_site_status=next(status),
    principal_investigator=next(principle_investigator),
    project_site_lead_nurses=next(lead_nurse),
) for s in study_names]

db.session.add_all(edge_studies)
db.session.commit()


# Studies
studies = [Study(name=es.project_short_title, edge_id=es.project_id, civicrm_study_id=cs.id) for es, cs in zip(edge_studies, civicrm_studies)]

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
