import ldap
from flask import (
    render_template,
    redirect,
    url_for,
    current_app,
    flash,
)
from sqlalchemy.sql import select
from .. import blueprint
from identity.emailing import email
from identity.database import pmi_engine
from dateutil.parser import parse


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


@blueprint.route("/dob_test")
def dob_test():
    flash('Yello')
    
    parsed_date = parse('19440203', dayfirst=True)
    flash(parsed_date)
    parsed_date = parse('19441219', dayfirst=True)
    flash(parsed_date)
    parsed_date = parse('19/12/1944', dayfirst=True)
    flash(parsed_date)
    parsed_date = parse('20/02/1957', dayfirst=True)
    flash(parsed_date)

    return redirect(url_for('ui.index'))
