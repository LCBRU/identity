from datetime import datetime
from flask_login import current_user
from .security import get_admin_role

def init_template_filters(app):
    @app.template_filter("yes_no")
    def yesno_format(value):
        if value is None:
            return ""
        if value:
            return "Yes"
        else:
            return "No"

    @app.template_filter("datetime_format")
    def datetime_format(value):
        if value:
            return value.strftime("%c")
        else:
            return ""

    @app.template_filter("date_format")
    def date_format(value):
        if value:
            return value.strftime("%-d %b %Y")
        else:
            return ""

    @app.template_filter("blank_if_none")
    def blank_if_none(value):
        return value or ""

    @app.template_filter("default_if_none")
    def default_if_none(value, default):
        return value or default

    @app.template_filter("currency")
    def currency(value):
        if value:
            return "£{:.2f}".format(value)
        else:
            return ""

    @app.context_processor
    def inject_now():
        return {'current_year': datetime.utcnow().strftime("%Y")}
