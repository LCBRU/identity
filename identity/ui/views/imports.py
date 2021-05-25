from sqlalchemy import func
from flask import render_template, redirect
from flask.helpers import url_for
from flask_security import roles_required
from identity.ecrfs.model import EcrfDetail
from lbrc_flask.database import db
from .. import blueprint


@blueprint.route("/imports")
@roles_required('admin')
def imports():
    ecrf_count = EcrfDetail.query.count()

    return render_template("ui/imports.html", ecrf_count=ecrf_count)


@blueprint.route("/delete_ecrfs", methods=['POST'])
@roles_required('admin')
def delete_ecrfs():
    for d in EcrfDetail.query.all():
        db.session.delete(d)

    db.session.commit()

    return redirect(url_for('ui.imports'))
