import datetime
import flask_admin as admin
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView, fields
from flask_login import current_user
from identity.database import db
from identity.model.security import (
    User,
    Role,
)
from identity.model import Study
from identity.redcap.model import (
    RedcapInstance,
    RedcapProject,
)
from identity.security import get_admin_role

class QuerySelectMultipleFieldSet(fields.QuerySelectMultipleField):
    def populate_obj(self, obj, name):
        setattr(obj, name, set(self.data))


class CustomView(ModelView):
    # Enable CSRF
    form_base_class = SecureForm

    def is_accessible(self):
        return get_admin_role() in current_user.roles


class UserView(CustomView):
    form_columns = ["username", "first_name", "last_name", "studies", "active", "roles"]

    # form_args and form_overrides required to allow studies and roles to be sets.
    form_args = {
        'studies': {
            'query_factory': lambda: db.session.query(Study)
        },
        'roles': {
            'query_factory': lambda: db.session.query(Role)
        },
    }
    form_overrides = {
        'studies': QuerySelectMultipleFieldSet,
        'roles': QuerySelectMultipleFieldSet,
    }


class StudyView(CustomView):
    can_delete = False
    can_edit = False
    form_columns = ["name"]


class RedcapInstanceView(CustomView):
    form_columns = ["name", "database_name", "base_url"]

    def on_model_change(self, form, model, is_created):
        model.last_updated_datetime = datetime.datetime.utcnow()
        model.last_updated_by_user = current_user


class RedcapProjectView(CustomView):
    form_columns = ["study", "redcap_instance", "project_id"]

    def on_model_change(self, form, model, is_created):
        model.last_updated_datetime = datetime.datetime.utcnow()
        model.last_updated_by_user = current_user


def init_admin(app):
    flask_admin = admin.Admin(app, name="Leicester BRC Identity", url="/admin")
    flask_admin.add_view(UserView(User, db.session))
    flask_admin.add_view(StudyView(Study, db.session))
    flask_admin.add_view(RedcapInstanceView(RedcapInstance, db.session))
    flask_admin.add_view(RedcapProjectView(RedcapProject, db.session))
