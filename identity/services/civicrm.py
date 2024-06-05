
from sqlalchemy import select
from lbrc_flask.database import db
from identity.model.civicrm import CiviCrmStudy


def get_civicrm_study_choices():
    q = select(CiviCrmStudy).where(CiviCrmStudy.is_active == True)
    return [(s.id, s.name) for s in db.session.execute(q).scalars()]


