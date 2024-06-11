from sqlalchemy import select
from lbrc_flask.database import db
from identity.model.civicrm import CiviCrmStudy, CiviCrmParticipant
from lbrc_flask.forms import SearchForm
from wtforms import BooleanField


class ParticipantSearchForm(SearchForm):
    show_deleted = BooleanField('Deleted')


def get_civicrm_study_choices():
    q = select(CiviCrmStudy).where(CiviCrmStudy.is_active == True).order_by(CiviCrmStudy.name)
    return [(s.id, s.name) for s in db.session.execute(q).scalars()]


def get_participant_query(form, study_id):
    q = select(CiviCrmParticipant).where(CiviCrmParticipant.study_id == study_id)
    return q
