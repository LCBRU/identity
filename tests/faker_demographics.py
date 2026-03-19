from functools import cache
import os
from random import choice
from faker.providers import BaseProvider
from lbrc_flask.pytest.faker import FakeCreator, FakeCreatorArgs
from identity.demographics.model import DemographicsRequest


class DemographicsRequestCreator(FakeCreator):

    @property
    def cls(self):
        return DemographicsRequest

    def _create_item(self, save, args: FakeCreatorArgs):
        extension: str = args.get('extension', choice(['xslx', 'xsl', 'csv']))

        params = dict(
            created_datetime=args.get('created_datetime', self.faker.date_object()),
            filename=args.get('filename', self.faker.file_name(extension=extension)),
            extension=args.get('extension', f".{extension}"),
            submitted_datetime=args.get('submitted_datetime', self.faker.date_object()),
            deleted_datetime=args.get('deleted_datetime', self.faker.date_object()),
            paused_datetime=args.get('paused_datetime', self.faker.date_object()),
            data_extracted_datetime=args.get('data_extracted_datetime', self.faker.date_object()),
            pmi_data_pre_completed_datetime=args.get('pmi_data_pre_completed_datetime', self.faker.date_object()),
            pmi_data_post_completed_datetime=args.get('pmi_data_post_completed_datetime', self.faker.date_object()),
            lookup_completed_datetime=args.get('lookup_completed_datetime', self.faker.date_object()),
            result_created_datetime=args.get('result_created_datetime', self.faker.date_object()),
            result_downloaded_datetime=args.get('result_downloaded_datetime', self.faker.date_object()),
            error_message=args.get('error_message', self.faker.sentence()),
            last_updated_datetime=args.get('last_updated_datetime', self.faker.date_object()),
            skip_pmi=args.get('skip_pmi', self.faker.pybool())
        )

        args.set_params_with_object(params, 'owner', field_id_name='owner_user_id', creator=self.faker.user())
        args.set_params_with_object(params, 'last_updated_by_user', creator=self.faker.user())

        return self.cls(**params)
    
    def create_file(self, demographics_request, content):
        os.makedirs(os.path.dirname(demographics_request.filepath), exist_ok=True)
        with open(demographics_request.filepath, 'w') as f:
            f.write(content)


class DemographicsProvider(BaseProvider):
    @cache
    def demographics_request(self):
        return DemographicsRequestCreator(self)
