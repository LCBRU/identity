from matplotlib.transforms import Bbox
from datetime import date
from operator import or_
from identity.model.edge import EdgeSiteStudy
from identity.ui.forms import TrackerSearchForm, TrackerSearchGanttForm
from flask import render_template, request, send_file
from .. import blueprint
from dateutil.relativedelta import relativedelta
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


@blueprint.route("/study_tracker/rag", methods=['GET', 'POST'])
def study_tracker_rag():
    if request.args:
        search_form = TrackerSearchForm(formdata=request.args)
    else:
        search_form = TrackerSearchForm()

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


@blueprint.route("/study_tracker/gantt", methods=['GET', 'POST'])
def study_tracker_gantt():
    if request.args:
        search_form = TrackerSearchGanttForm(formdata=request.args)
    else:
        search_form = TrackerSearchGanttForm()

    return render_template("ui/study_tracker/gantt.html", search_form=search_form)


@blueprint.route("/study_tracker/gantt/image")
def study_tracker_gantt_image():
    if request.args:
        search_form = TrackerSearchGanttForm(formdata=request.args)
    else:
        search_form = TrackerSearchGanttForm()

    q = _get_edge_site_search_query(search_form)

    start_date = date(int(search_form.start_year.data), 1, 1)
    years = int(search_form.period.data)
    end_date = start_date + relativedelta(years=years)
    
    q = q.filter(EdgeSiteStudy.effective_recruitment_start_date != None)
    q = q.filter(EdgeSiteStudy.effective_recruitment_start_date <= end_date)
    q = q.filter(EdgeSiteStudy.effective_recruitment_end_date != None)
    q = q.filter(EdgeSiteStudy.effective_recruitment_end_date >= start_date)

    gc = GanttChart(
        start_date=start_date,
        years=years,
        studies=q.all(),
    )

    return gc.send_png(filename='tracker.png')


class GanttChart():
    WIDTH_PX = 1200
    STUDY_BAR_HEIGHT = 50
    STUDY_TEXT_HEIGHT = 30
    STUDY_HEIGHT_PX = STUDY_BAR_HEIGHT + STUDY_TEXT_HEIGHT
    MIN_HEIGHT_PX = 200

    TICK_PARAMS = {
        1: {
            'major_locator':  mdates.MonthLocator(interval=1),
            'minor_locator':   mdates.MonthLocator(interval=1),
            'format': mdates.DateFormatter('%b %Y')
        },
        2: {
            'major_locator':  mdates.MonthLocator(interval=6),
            'minor_locator':   mdates.MonthLocator(interval=1),
            'format': mdates.DateFormatter('%b %Y')
        },
        3: {
            'major_locator':  mdates.MonthLocator(interval=6),
            'minor_locator':  mdates.MonthLocator(interval=1),
            'format': mdates.DateFormatter('%b %Y')
        },
        4: {
            'major_locator':  mdates.MonthLocator(interval=12),
            'minor_locator':  mdates.MonthLocator(interval=6),
            'format': mdates.DateFormatter('%b %Y')
        },
        5: {
            'major_locator':  mdates.MonthLocator(interval=12),
            'minor_locator':  mdates.MonthLocator(interval=6),
            'format': mdates.DateFormatter('%b %Y')
        },
    }

    def __init__(self, start_date, years, studies):
        self.start_date = start_date
        self.years = years
        self.end_date = self.start_date + relativedelta(years=self.years)
        self.data = self._gantt_data_from_studies(studies)
        self.height = max(len(self.data) * GanttChart.STUDY_HEIGHT_PX, GanttChart.MIN_HEIGHT_PX)


    def send_png(self, filename):
        plt = self.graph()
        buf = io.BytesIO()
        plt.savefig(buf)
        buf.seek(0)

        return send_file(buf, attachment_filename=filename)

    def graph(self):
        fig, ax = plt.subplots()
        plt.subplots_adjust(left=0.03, right=0.97, top=0.99, bottom=0.1)
        renderer = fig.canvas.get_renderer()

        fig.set_size_inches(
            GanttChart.WIDTH_PX / 100,
            self.height / 100,
        )

        plt.grid(
            axis='x',
            which='major',
            visible=True,
            color='0.8',
        )
        plt.grid(
            axis='x',
            which='minor',
            visible=True,
            color='0.9',
            linestyle='--',
        )
        plt.tick_params(
            axis='y',
            which='both',
            left=False,
            right=False,
            labelleft=False,
        )

        # X Axes
        ax2 = ax.twiny()

        for x in [ax, ax2]:
            x.xaxis.set_major_locator(GanttChart.TICK_PARAMS[self.years]['major_locator'])
            x.xaxis.set_minor_locator(GanttChart.TICK_PARAMS[self.years]['minor_locator'])
            x.xaxis.set_major_formatter(GanttChart.TICK_PARAMS[self.years]['format'])
            x.set_xlim(self.start_date, self.end_date)

        # Y Axis
        ax.set_ylim(0, self.height)

        for i, d in enumerate(self.data, 1):
            top = self.height - (i * GanttChart.STUDY_HEIGHT_PX)
            left = max(d['start_date'], self.start_date)

            t = plt.text(
                0,
                0,
                d['name'],
                ha="left",
                va="bottom",
            )

            bbox = Bbox(ax.transData.inverted().transform(t.get_window_extent(renderer=renderer)))

            if (left + relativedelta(days=bbox.width)) > self.end_date:
                t._x = self.end_date - relativedelta(days=bbox.width)
            else:
                t._x = left

            t._y = top + GanttChart.STUDY_BAR_HEIGHT
    
            ax.broken_barh(
                [(d['start_date'], d['duration'])],
                (top, GanttChart.STUDY_BAR_HEIGHT),
                # facecolors =('tab:orange'),
            )

        return plt

    def _gantt_data_from_studies(self, studies):
        result = []

        for x in studies:
            result.append({
                'name': x.project_short_title,
                'start_date': x.effective_recruitment_start_date,
                'duration': (x.effective_recruitment_end_date - x.effective_recruitment_start_date).days,
            })

        return result
