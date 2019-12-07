import ldap
from flask import (
    render_template,
    redirect,
    url_for,
    current_app,
)
from .. import blueprint
from identity.emailing import email

@blueprint.route("/email")
def email_test():
    email(
        subject='Identity Email test',
        recipients=['richard.a.bramley@uhl-tr.nhs.uk'],
        message='Hello'
    )

    return redirect(url_for('ui.index'))
