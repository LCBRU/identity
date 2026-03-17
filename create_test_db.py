#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()

from tests.faker import IdentityProvider
from tests.faker_civicrm import CivicrmProvider
from tests.faker_etl_central import EtlCentralProvider
from lbrc_flask.database import db
from lbrc_flask.security import init_roles, init_users
from identity.setup import setup_data
from faker import Faker
from alembic.config import Config
from alembic import command
from lbrc_flask.pytest.faker import LbrcFlaskFakerProvider
from identity import create_app


fake = Faker("en_GB")
fake.add_provider(LbrcFlaskFakerProvider)
fake.add_provider(IdentityProvider)
fake.add_provider(CivicrmProvider)
fake.add_provider(EtlCentralProvider)

application = create_app()
application.app_context().push()
db.create_all()
init_roles([])
init_users()

alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")

setup_data()

fake.civicrm_gender().create_defaults()
fake.civicrm_gender().all_from_db()
fake.civicrm_case_status().create_defaults()
fake.civicrm_case_status().all_from_db()
fake.civicrm_study().create_defaults()

fake.civicrm_participant().get_list(
    save=True,
    item_count=200,
    study=fake.civicrm_study().choice_from_db,
    status=fake.civicrm_case_status().choice_from_db,
)

for cs in fake.civicrm_study().all_from_db():
    es = fake.edge_site_study().get(
        save=True,
        project_short_title=cs.name,
    )

    fake.study().get(
        save=True,
        name=cs.name,
        edge_id=es.project_id,
        civicrm_study_id=cs.id,
    )

fake.label_bundle().get_list(save=True, item_count=fake.study().count_in_db() * 3, study=fake.study().choice_from_db)
fake.blinding_type().get_list(save=True, item_count=fake.study().count_in_db() * 3, study=fake.study().choice_from_db)

db.session.close()
