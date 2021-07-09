from operator import or_
from lbrc_edge import EdgeSiteStudy
from identity.ui.forms import TrackerRagSearchForm
from flask import render_template, request
from .. import blueprint


@blueprint.route("/study_tracker/rag", methods=['GET', 'POST'])
def study_tracker_rag():
    search_form = TrackerRagSearchForm(formdata=request.args)

    ess = _get_edge_site_search_query(search_form).paginate(
        page=search_form.page.data, per_page=10, error_out=False
    )

    return render_template("ui/study_tracker/rag.html", search_form=search_form, edge_site_studies=ess)


def _get_edge_site_search_query(search_form):
    q = EdgeSiteStudy.query

    if search_form.search.data:
        title_search = EdgeSiteStudy.project_short_title.like('%{}%'.format(search_form.search.data))
        if search_form.search.data.isnumeric():
            q = q.filter(or_(title_search, EdgeSiteStudy.project_id == search_form.search.data))
        else:
            q = q.filter(title_search)

    if search_form.clinical_area.data:
        q = q.filter(EdgeSiteStudy.primary_clinical_management_areas.in_(search_form.clinical_area.data))

    if search_form.status.data:
        q = q.filter(EdgeSiteStudy.project_site_status.in_(search_form.status.data))

    if search_form.principal_investigator.data:
        q = q.filter(EdgeSiteStudy.principal_investigator == search_form.principal_investigator.data)

    if search_form.lead_nurse.data:
        q = q.filter(EdgeSiteStudy.project_site_lead_nurses == search_form.lead_nurse.data)

    return q.order_by(EdgeSiteStudy.project_short_title)