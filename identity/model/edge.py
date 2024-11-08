from lbrc_flask.database import db
from datetime import datetime, date
import math


class EdgeSiteStudy(db.Model):
    __tablename__ = 'edge_site_study'
    __bind_key__ = 'etl_central'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer)
    iras_number = db.Column(db.String(50))
    project_short_title = db.Column(db.String(200))
    primary_clinical_management_areas = db.Column(db.String(200))
    project_site_status = db.Column(db.String(100))
    project_site_rand_submission_date = db.Column(db.Date)
    project_site_start_date_nhs_permission = db.Column(db.Date)
    project_site_date_site_confirmed = db.Column(db.Date)
    project_site_planned_closing_date = db.Column(db.Date)
    project_site_closed_date = db.Column(db.Date)
    project_site_planned_recruitment_end_date = db.Column(db.Date)
    project_site_actual_recruitment_end_date = db.Column(db.Date)
    principal_investigator = db.Column(db.String(200))
    project_site_target_participants = db.Column(db.Integer)
    recruited_org = db.Column(db.Integer)
    project_site_lead_nurses = db.Column(db.String(200))

    planned_start_date = db.Column(db.Date)
    planned_end_date = db.Column(db.Date)

    # calculated fields
    effective_recruitment_start_date = db.Column(db.Date)
    effective_recruitment_end_date = db.Column(db.Date)

    target_end_date = db.Column(db.Date)
    target_end_date_description = db.Column(db.String(500))
    target_requirement_by = db.Column(db.Integer)

    current_target_recruited_percent = db.Column(db.Integer)
    rag_rating = db.Column(db.String(100))

    def calculate_values(self):
        self._calculate_effective_recruitment_start_date()
        self._calculate_effective_recruitment_end_date()
        self._calculate_target_end_date()
        self._calculate_target_end_date_description()
        self._calculate_target_requirement_by()
        self._calculate_current_target_recruited_percent()
        self._calculate_rag_rating()

    def _calculate_effective_recruitment_start_date(self):
        result = self.project_site_start_date_nhs_permission or self.project_site_date_site_confirmed

        if result:
            self.effective_recruitment_start_date = date(result.year, result.month, result.day)    
        else:
            self.effective_recruitment_start_date = None

    def _calculate_effective_recruitment_end_date(self):
        result = self.project_site_actual_recruitment_end_date or self.project_site_planned_recruitment_end_date

        if result:
            self.effective_recruitment_end_date = date(result.year, result.month, result.day)
        else:
            self.effective_recruitment_end_date = None
    
    def _calculate_target_end_date(self):
        self.target_end_date = min(datetime.now().date(), (self.effective_recruitment_end_date or datetime.max.date()))

    def _calculate_target_end_date_description(self):
        if datetime.now().date() < (self.effective_recruitment_end_date or datetime.max.date()):
            self.target_end_date_description = 'today'
        else:
            self.target_end_date_description = 'study end date'

    def _calculate_target_requirement_by(self):
        if self.effective_recruitment_start_date is None or self.project_site_target_participants is None or self.effective_recruitment_end_date is None:
            self.target_requirement_by = None
        else:
            self.target_requirement_by = int(math.ceil(self.project_site_target_participants * (self.effective_recruitment_start_date - self.target_end_date).days / (self.effective_recruitment_start_date - self.effective_recruitment_end_date).days))

    def _calculate_current_target_recruited_percent(self):
        if not self.target_requirement_by:
            self.current_target_recruited_percent = None
        else:
            recruited = self.recruited_org or 0

            self.current_target_recruited_percent = round(recruited * 100 / self.target_requirement_by, 0)

    def _calculate_rag_rating(self):
        if self.current_target_recruited_percent is None:
            self.rag_rating = None
        else:
            if self.current_target_recruited_percent >= 100:
                self.rag_rating = 'success'
            elif self.current_target_recruited_percent < 80:
                self.rag_rating = 'danger'
            else:
                self.rag_rating = 'warning'

    @property
    def rag_code(self):
        if self.rag_rating == 'success':
            return "G"
        elif self.rag_rating == 'danger':
            return "R"
        elif self.rag_rating == 'warning':
            return "A"

    @property
    def rag_class(self):
        if self.rag_rating == 'success':
            return "success"
        elif self.rag_rating == 'danger':
            return "error"
        elif self.rag_rating == 'warning':
            return "warning"
        else:
            return "muted"


    def study_dates(self):
        result = {}

        if self.project_site_rand_submission_date is not None:
            result['Project Site R&D Submission Date'] = self.project_site_rand_submission_date
        if self.project_site_start_date_nhs_permission is not None:
            result['Project Site Start Date (NHS Permission)'] = self.project_site_start_date_nhs_permission
        if self.project_site_date_site_confirmed is not None:
            result['Project Site Date Site Confirmed'] = self.project_site_date_site_confirmed
        if self.project_site_planned_closing_date is not None:
            result['Project Site Planned Closing Date'] = self.project_site_planned_closing_date
        if self.project_site_closed_date is not None:
            result['Project Site Closed Date'] = self.project_site_closed_date
        if self.project_site_planned_recruitment_end_date is not None:
            result['Project Site Planned Recruitment End Date'] = self.project_site_planned_recruitment_end_date
        if self.project_site_actual_recruitment_end_date is not None:
            result['Project Site Actual Recruitment End Date'] = self.project_site_actual_recruitment_end_date
        if self.planned_start_date is not None:
            result['Planned Start Date'] = self.planned_start_date
        if self.planned_end_date is not None:
            result['Planned End Date'] = self.planned_end_date

        return {k: v for k, v in sorted(result.items(), key=lambda item: date(item[1].year, item[1].month, item[1].day))}

    @property
    def key_staff(self):
        staff = []

        if self.principal_investigator:
            staff.append(f'Principal Investigator: {self.principal_investigator}')

        if self.project_site_lead_nurses:
            staff.append(f'Lead Nurse: {self.project_site_lead_nurses}')

        return '; '.join(staff)
