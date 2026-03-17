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


faker = Faker("en_GB")
faker.add_provider(LbrcFlaskFakerProvider)
faker.add_provider(IdentityProvider)
faker.add_provider(CivicrmProvider)
faker.add_provider(EtlCentralProvider)

application = create_app()
application.app_context().push()
db.create_all()
init_roles([])
init_users()

alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")

setup_data()

faker.civicrm_gender().create_defaults()
faker.civicrm_gender().all_from_db()
faker.civicrm_case_status().create_defaults()
faker.civicrm_case_status().all_from_db()
faker.civicrm_study().create_defaults()

faker.civicrm_participant().get_list(
    save=True,
    item_count=200,
    study=faker.civicrm_study().choice_from_db,
    status=faker.civicrm_case_status().choice_from_db,
)

for cs in faker.civicrm_study().all_from_db():
    es = faker.edge_site_study().get(
        save=True,
        project_short_title=cs.name,
    )

    faker.study().get(
        save=True,
        name=cs.name,
        edge_id=es.project_id,
        civicrm_study_id=cs.id,
    )

faker.label_bundle().get_list(save=True, item_count=faker.study().count_in_db() * 3, study=faker.study().choice_from_db)
faker.blinding_type().get_list(save=True, item_count=faker.study().count_in_db() * 3, study=faker.study().choice_from_db)

db.session.close()
