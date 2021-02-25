from flask import render_template, redirect, url_for
from .. import blueprint
from lbrc_flask.emailing import email

@blueprint.route("/")
def index():
    return render_template("ui/index.html")
