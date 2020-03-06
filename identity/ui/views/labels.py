import time
import traceback
from itertools import chain
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    abort,
)
from flask_login import current_user
from identity.printing.model import LabelPack
from .. import blueprint, db
from ..decorators import assert_study_user


@blueprint.route("/labels/")
def labels():
    return render_template(
        "ui/labels.html",
        label_sets=chain.from_iterable(s.label_packs for s in current_user.studies),
        studies=current_user.studies,
    )


@blueprint.route("/labels/print/<string:set>/<int:count>?referrer=<string:referrer>&study_id=<int:study_id>")
@assert_study_user()
def label_print(set, referrer, study_id, count=1):
    label_pack = LabelPack.query.filter_by(type=set).first()

    if current_user not in label_pack.study.users:
        abort(403)

    try:
        label_pack.print(count)
        flash('Labels have been sent to the printer')
    except:
        current_app.logger.error(traceback.format_exc())
        flash("An error occurred while printing.  Check that the printer has paper and ink, and that a jam has not occurred.", "error")
    finally:
        if referrer == 'study' and study_id is not None:
            return redirect(url_for('ui.study', id=study_id))
        else:
            return redirect(url_for("ui.labels"))
