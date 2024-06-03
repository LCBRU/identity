#!/usr/bin/env python3

from random import randint
from dotenv import load_dotenv
from lbrc_flask.database import db
from lbrc_flask.security import init_roles, init_users
from identity.model import Study
from identity.printing import LabelBundle
from identity.setup import setup_data

load_dotenv()

from identity import create_app

application = create_app()
application.app_context().push()
db.create_all()
init_roles([])
init_users()

setup_data()

studies = [Study(name=s) for s in ['GENVASC', 'BRICCS', 'STEVEDORE']]

db.session.add_all(studies)
db.session.commit()

bundles = []
for s in studies:
    bundles.extend([LabelBundle(name=f'{s.name} {i}', study_id=s.id) for i in range(1, randint(1, 5))])

db.session.add_all(bundles)
db.session.commit()

db.session.close()
