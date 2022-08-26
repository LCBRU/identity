from flask_login import current_user

from identity.model import Study

def init_template_filters(app):
    @app.context_processor
    def inject_stuff():
        user_studies = []

        if not current_user.is_anonymous:
            if current_user.is_admin:
                user_studies = Study.query.all()
            else:
                user_studies = current_user.studies

        return {
            'user_studies': user_studies,
        }
