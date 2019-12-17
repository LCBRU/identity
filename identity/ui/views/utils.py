import ldap
from flask import (
    render_template,
    redirect,
    url_for,
    current_app,
)
from sqlalchemy.sql import select
from .. import blueprint
from identity.emailing import email
from identity.database import pmi_engine

@blueprint.route("/email")
def email_test():
    email(
        subject='Identity Email test',
        recipients=['richard.a.bramley@uhl-tr.nhs.uk'],
        message='Hello'
    )

    return redirect(url_for('ui.index'))

@blueprint.route("/pmi")
def pmi_test():
    with pmi_engine() as conn:
        s_dets = conn.execute("SELECT * FROM [dbo].[UHL_PMI_QUERY_BY_ID]('S0470673')")

        print(s_dets)

    return redirect(url_for('ui.index'))
