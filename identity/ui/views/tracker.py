import altair as alt
import pandas as pd
from datetime import datetime, date
from operator import or_
from lbrc_edge import EdgeSiteStudy
from identity.ui.forms import TrackerSearchForm, TrackerSearchGanttForm
from flask import render_template, request
from .. import blueprint
from dateutil.relativedelta import relativedelta


@blueprint.route("/study_tracker/rag", methods=['GET', 'POST'])
def study_tracker_rag():
    search_form = TrackerSearchForm(formdata=request.args)

    ess = _get_edge_site_search_query(search_form).paginate(
        page=search_form.page.data, per_page=10, error_out=False
    )

    return render_template("ui/study_tracker/rag.html", search_form=search_form, edge_site_studies=ess)


@blueprint.route("/study_tracker/gantt", methods=['GET', 'POST'])
def study_tracker_gantt():
    search_form = TrackerSearchGanttForm(formdata=request.args)

    return render_template("ui/study_tracker/gantt.html", search_form=search_form, gantt_chart=study_tracker_gantt_image(search_form))


def study_tracker_gantt_image(search_form):
    edge_studies_query = _get_edge_site_search_query(search_form)

    edge_studies = edge_studies_query.all()

    start_date = date(int(search_form.start_year.data), 1, 1)
    end_date = start_date + relativedelta(years=int(search_form.period.data))

    data = _gantt_data_from_studies(edge_studies, start_date, end_date)
    df = pd.DataFrame(data)

    bar_chart = alt.Chart(df).mark_bar(size=30).encode(
        x=alt.X(
            "Start",
            axis=_get_gantt_xaxis_definition(start_date, search_form.period.data),
        ),
        x2="End",
        y=alt.Y(
            "Task",
            axis=None,
            sort=list(
                df.sort_values(["Start"])
                ["Task"],
            )
        ),
        color=alt.Color("Status"),
    ).properties(
        width=1000,
        height=len(data) * 60,
    )

    bar_chart_text = bar_chart.mark_text(
        align='left',
        dy=-20,
    ).encode(
        text="Task",
    )

    return (bar_chart_text + bar_chart).to_json()

def _get_gantt_xaxis_definition(start_date, period):
    periods = int(period) * 12
    date_ticks = [d.isoformat() for d in pd.date_range(start_date, freq='1M', periods=periods)]

    return alt.Axis(
        values=date_ticks,
        format="%b %Y",
        tickCount=periods,
        labelAngle=90,
        title='',
    )

def _gantt_data_from_studies(studies, start_date, end_date):
    result = []

    for x in studies:
        if x.effective_recruitment_start_date is None or x.effective_recruitment_end_date is None:
            continue

        if x.effective_recruitment_start_date > end_date or x.effective_recruitment_end_date < start_date:
            continue

        s_date = max(x.effective_recruitment_start_date, start_date)
        e_date = min(x.effective_recruitment_end_date, end_date)

        result.append(        {
            'Task': x.project_short_title,
            'Start': datetime.combine(s_date, datetime.min.time()),
            'End': datetime.combine(e_date, datetime.min.time()),
            'Status': x.project_site_status,
        })

    return result


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