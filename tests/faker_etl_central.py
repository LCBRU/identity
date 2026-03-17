from datetime import timedelta
from functools import cache
from random import choice
from faker.providers import BaseProvider
from lbrc_flask.pytest.faker import FakeCreator, FakeCreatorArgs
from identity.model.edge import EdgeSiteStudy


class EdgeSiteStudyCreator(FakeCreator):

    @property
    def cls(self):
        return EdgeSiteStudy

    def _create_item(self, save, args: FakeCreatorArgs):
        start_date = args.get('project_site_start_date_nhs_permission', self.faker.date_object())
        study_length = self.faker.pyint(30, 600)
        end_date = start_date + timedelta(days=study_length)

        if self.faker.pyint(1, 100) < 75:
            target_recruitment=10 * self.faker.pyint(1, 100)
        else:
            target_recruitment=None

        params = dict(
            project_id=self.faker.unique.ean(length=8),
            iras_number=self.faker.unique.license_plate(),
            project_short_title=args.get('project_short_title', self.faker.unique.word()),
            primary_clinical_management_areas=args.get('primary_clinical_management_areas', self.faker.word()),
            project_site_status=args.get('primary_clinical_management_areas', choice(['Cancel', 'Loaded', 'Deleted'])),
            principal_investigator=args.get('principal_investigator', self.faker.name()),
            project_site_lead_nurses=args.get('project_site_lead_nurses', self.faker.name()),

            project_site_rand_submission_date=args.get('project_site_rand_submission_date', self.faker.date_object()),
            project_site_start_date_nhs_permission=start_date,
            project_site_date_site_confirmed=start_date + timedelta(days=self.faker.pyint(-10,10)),
            project_site_planned_closing_date=args.get('project_site_planned_closing_date', self.faker.date_object()),
            project_site_closed_date=args.get('project_site_closed_date', self.faker.date_object()),
            project_site_actual_recruitment_end_date=end_date,
            project_site_planned_recruitment_end_date=end_date + timedelta(days=self.faker.pyint(-10,10)),
            project_site_target_participants=target_recruitment,
        )

        result = self.cls(**params)

        result.calculate_values()
        result.recruited_org = int(result.target_requirement_by or 0) * choice([0.1,0.5,0.6,0.8,0.85,0.9,0.95,1,1.05,1.10,1.50])
        result.calculate_values()

        return result


class EtlCentralProvider(BaseProvider):
    @cache
    def edge_site_study(self):
        return EdgeSiteStudyCreator(self)
