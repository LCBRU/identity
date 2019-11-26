from flask import render_template, redirect, url_for
from .. import blueprint
from identity.emailing import email

@blueprint.route("/")
def index():
    return render_template("ui/index.html")


@blueprint.route("/email")
def email_test():
    email(
        subject='Identity Email test',
        recipients=['richard.a.bramley@uhl-tr.nhs.uk'],
        message='Hello'
    )

    return redirect(url_for('ui.index'))
