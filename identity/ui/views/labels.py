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
from .. import blueprint, db
from identity.printing.model import LabelPack


@blueprint.route("/labels/")
def labels():
    return render_template(
        "ui/labels.html",
        label_sets=chain.from_iterable(s.label_packs for s in current_user.studies),
        studies=current_user.studies,
    )


@blueprint.route("/labels/print/<string:set>/<int:count>")
def label_print(set, count=1):
    label_pack = LabelPack.query.filter_by(type=set).first()

    if current_user not in label_pack.study.users:
        abort(403)

    try:
        for _ in range(count):
            label_pack.print()

            db.session.commit()

            time.sleep(current_app.config['PRINTING_SET_SLEEP'])
    except:
        current_app.logger.error(traceback.format_exc())
        flash("An error occurred while printing.  Check that the printer has paper and ink, and that a jam has not occurred.", "error")
    finally:
        return redirect(url_for("ui.labels"))
