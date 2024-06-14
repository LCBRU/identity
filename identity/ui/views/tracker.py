from matplotlib.transforms import Bbox
from datetime import date
from operator import or_
from identity.model.edge import EdgeSiteStudy
from flask import render_template, request, send_file
from .. import blueprint
from dateutil.relativedelta import relativedelta
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from lbrc_flask.export import pdf_download
from calendar import monthrange
from datetime import datetime
from wtforms import SelectField, SelectMultipleField
from lbrc_flask.forms import SearchForm
from identity.model.edge import EdgeSiteStudy


def _get_clinical_area_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.primary_clinical_management_areas.distinct()).all()
    return [(s[0], s[0]) for s in ess]


def _get_status_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.project_site_status.distinct()).all()
    return [(s[0], s[0]) for s in ess]


def _get_principal_investigator_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.principal_investigator.distinct()).all()
    return [('', '')] + [(s, s) for s in sorted(filter(None, [s[0] for s in ess]))]


def _get_lead_nurse_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.project_site_lead_nurses.distinct()).all()
    return [('', '')] + [(s, s) for s in sorted(filter(None, [s[0] for s in ess]))]


def _get_rag_rating_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.rag_rating.distinct()).all()
    return [('', '')] + [(s, s.title()) for s in sorted(filter(None, [s[0] for s in ess]))]


class TrackerSearchForm(SearchForm):
    clinical_area = SelectMultipleField('Clinical Area', choices=[])
    status = SelectMultipleField('Status', choices=[], default=['Open'])
    principal_investigator = SelectField('Principal Investigator', choices=[])
    lead_nurse = SelectField('Lead Nurse', choices=[])
    rag_rating = SelectField('RAG Rating', choices=[])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.clinical_area.choices = _get_clinical_area_choices()
        self.status.choices = _get_status_choices()
        self.principal_investigator.choices = _get_principal_investigator_choices()
        self.lead_nurse.choices = _get_lead_nurse_choices()
        self.rag_rating.choices = _get_rag_rating_choices()


class TrackerSearchGanttForm(TrackerSearchForm):
    start_year = SelectField('Start Date', choices=[], default=datetime.now().year)
    period = SelectField('Period', choices=[(1, '1 year'), (2, '2 years'), (3, '3 years'), (4, '4 years'), (5, '5 years')], default=1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        this_year = datetime.now().year
        self.start_year.choices = [(y, y) for y in range(this_year - 10, this_year + 10)]


@blueprint.route("/study_tracker/rag", methods=['GET', 'POST'])
def study_tracker_rag():
    search_form = TrackerSearchForm(formdata=request.args, search_placeholder='Search Studies')

    ess = _get_edge_site_search_query(search_form).paginate(
        page=search_form.page.data, per_page=10, error_out=False
    )

    return render_template("ui/study_tracker/rag.html", search_form=search_form, edge_site_studies=ess)


@blueprint.route("/study_tracker/rag/pdf")
def study_tracker_rag_pdf():
    search_form = TrackerSearchForm(formdata=request.args)

    ess = _get_edge_site_search_query(search_form).all()

    return pdf_download("ui/study_tracker/rag_pdf.html", title='study_tracker_rag', edge_site_studies=ess)


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

    if search_form.rag_rating.data:
        q = q.filter(EdgeSiteStudy.rag_rating == search_form.rag_rating.data)

    return q.order_by(EdgeSiteStudy.project_short_title)


@blueprint.route("/study_tracker/gantt", methods=['GET', 'POST'])
def study_tracker_gantt():
    search_form = TrackerSearchGanttForm(formdata=request.args, search_placeholder='Search Studies')

    return render_template("ui/study_tracker/gantt.html", search_form=search_form)


@blueprint.route("/study_tracker/gantt2", methods=['GET', 'POST'])
def study_tracker_gantt2():
    search_form = TrackerSearchGanttForm(formdata=request.args, search_placeholder='Search Studies')

    return render_template("ui/study_tracker/gantt2.html", search_form=search_form)


class Periodiser:
    def __init__(self, start_year, years):

        self.start_year = start_year
        self.start_date = date(self.start_year, 1, 1)
        self.years = years
        self.end_date = self.start_date + relativedelta(years=self.years)

    def pre_start_period(self, the_date):
        return 1 if the_date < self.start_date else 0
    
    def post_end_period(self, the_date):
        return 1 if the_date >= self.end_date else 0
    
    def start_period(self, the_date):
        if self.pre_start_period(the_date):
            return 0
        else:
            if self.period(the_date) in self.periods:
                return self.periods.index(self.period(the_date))

    def end_period(self, the_date):
        if self.post_end_period(the_date):
            return len(self.periods) - 1
        else:
            if self.period(the_date) in self.periods:
                return self.periods.index(self.period(the_date))

    def calc_period_perc(self, the_date):
        if self.pre_start_period(the_date):
            return 0
        elif self.post_end_period(the_date):
            return 100
        else:
            return self._calc_period_perc(the_date)


class PeriodiserYear(Periodiser):
    def __init__(self, start_year, years):
        super().__init__(start_year, years)

        self.periods = [p for p in range(self.start_date.year, self.end_date.year)]

    def period(self, the_date):
        return the_date.year

    def _calc_period_perc(self, the_date):
        return int(the_date.timetuple().tm_yday * 100 / 365)


class PeriodiserMonth(Periodiser):
    def __init__(self, start_year, years):
        super().__init__(start_year, years)

        self.periods = [date(start_year, p, 1).strftime('%b') for p in range(1, 13)]

    def period(self, the_date):
        return the_date.strftime('%b')

    def _calc_period_perc(self, the_date):
        return int(the_date.day * 100 / monthrange(the_date.year, the_date.month)[1] )


@blueprint.route("/study_tracker/gantt/json")
def study_tracker_gantt_json():
    search_form = TrackerSearchGanttForm(formdata=request.args)

    q = _get_edge_site_search_query(search_form)

    years = int(search_form.period.data)

    if years == 1:
        p = PeriodiserMonth(start_year=int(search_form.start_year.data), years=years)
    else:
        p = PeriodiserYear(start_year=int(search_form.start_year.data), years=years)

    q = q.filter(EdgeSiteStudy.effective_recruitment_start_date != None)
    q = q.filter(EdgeSiteStudy.effective_recruitment_start_date < p.end_date)
    q = q.filter(EdgeSiteStudy.effective_recruitment_end_date != None)
    q = q.filter(EdgeSiteStudy.effective_recruitment_end_date >= p.start_date)

    result = {
        'period': p.periods,
        'studies': [{
            'name': s.project_short_title,
            'start_date': s.effective_recruitment_start_date,
            'pre_start_period': p.pre_start_period(s.effective_recruitment_start_date),
            'start_period': p.start_period(s.effective_recruitment_start_date),
            'start_period_perc': p.calc_period_perc(s.effective_recruitment_start_date),
            'end_date': s.effective_recruitment_end_date,
            'post_end_period': p.post_end_period(s.effective_recruitment_end_date),
            'end_period': p.end_period(s.effective_recruitment_end_date),
            'end_period_perc': p.calc_period_perc(s.effective_recruitment_end_date),
            'class': 'info',
            'url': f'https://www.edge.nhs.uk/Project/Details/{s.project_id}',
        } for s in q.all()],
    }

    return result


@blueprint.route("/study_tracker/gantt/image")
def study_tracker_gantt_image():
    search_form = TrackerSearchGanttForm(formdata=request.args)

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

        return send_file(
            buf,
            as_attachment=True,
            download_name=filename,
            max_age=0,
            mimetype='image/png',
        )


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
