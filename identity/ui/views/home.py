from flask import render_template
from flask_login import current_user
from sqlalchemy import select

from identity.model import Study
from .. import blueprint, db


@blueprint.route("/")
def index():
    if current_user.is_admin:
        studies = db.session.execute(select(Study).order_by(Study.name)).unique().scalars()
    else:
        studies = current_user.studies

    return render_template(
        "ui/index.html",
        studies=studies,
    )
