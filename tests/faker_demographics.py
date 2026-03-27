from functools import cache
import os
from random import choice
from faker.providers import BaseProvider
from lbrc_flask.pytest.faker import FakeCreator, FakeCreatorArgs
from identity.demographics.model import DemographicsRequest, DemographicsRequestColumn, DemographicsRequestColumnDefinition, DemographicsRequestCsv, DemographicsRequestData, DemographicsRequestExcel97, DemographicsRequestPmiData, DemographicsRequestXlsx


class DemographicsRequestCreator(FakeCreator):

    @property
    def cls(self):
        return DemographicsRequest

    def _create_item(self, save, args: FakeCreatorArgs):
        extension: str = args.get('extension', choice(['xslx', 'xsl', 'csv']))

        if extension == 'xlsx': extension = 'xslx'
        if extension == 'xls': extension = 'xsl'

        params = dict(
            created_datetime=args.get('created_datetime', self.faker.date_object()),
            filename=args.get('filename', self.faker.file_name(extension=extension)),
            submitted_datetime=args.get('submitted_datetime'),
            deleted_datetime=args.get('deleted_datetime'),
            paused_datetime=args.get('paused_datetime'),
            data_extracted_datetime=args.get('data_extracted_datetime'),
            pmi_data_pre_completed_datetime=args.get('pmi_data_pre_completed_datetime'),
            pmi_data_post_completed_datetime=args.get('pmi_data_post_completed_datetime'),
            lookup_completed_datetime=args.get('lookup_completed_datetime'),
            result_created_datetime=args.get('result_created_datetime'),
            result_downloaded_datetime=args.get('result_downloaded_datetime'),
            error_message=args.get('error_message', self.faker.sentence()),
            last_updated_datetime=args.get('last_updated_datetime', self.faker.date_object()),
            skip_pmi=args.get('skip_pmi', self.faker.pybool())
        )

        args.set_params_with_object(params, 'owner', field_id_name='owner_user_id', creator=self.faker.user())
        args.set_params_with_object(params, 'last_updated_by_user', creator=self.faker.user())

        match extension:
            case 'csv':
                return DemographicsRequestCsv(**params)
            case 'xsl':
                return DemographicsRequestExcel97(**params)
            case 'xslx':
                return DemographicsRequestXlsx(**params)
    
    def get_csv(self, save, **kwargs):
        kwargs['extension'] = 'csv'
        return self.get(save, **kwargs)

    def get_xls(self, save, **kwargs):
        kwargs['extension'] = 'xls'
        return self.get(save, **kwargs)

    def get_xlsx(self, save, **kwargs):
        kwargs['extension'] = 'xlsx'
        return self.get(save, **kwargs)

    def create_file(self, demographics_request: DemographicsRequest, headers: list[str], data: list[dict]):
        os.makedirs(os.path.dirname(demographics_request.filepath), exist_ok=True)

        creator = self.faker.csv_file()
        match demographics_request:
            case DemographicsRequestXlsx():
                creator = self.faker.xlsx_file()
            case DemographicsRequestExcel97():
                creator = self.faker.xls_file()

        file = creator.get(
            headers=headers,
            data=data,
        )
        file.save(demographics_request.filepath)


class DemographicsRequestColumnCreator(FakeCreator):
    @property
    def cls(self):
        return DemographicsRequestColumn

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            name=args.get('name', self.faker.unique.word()),
        )

        args.set_params_with_object(params, 'demographics_request', creator=self.faker.demographics_request())

        return self.cls(**params)


class DemographicsRequestColumnDefinitionCreator(FakeCreator):
    @property
    def cls(self):
        return DemographicsRequestColumnDefinition

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            uhl_system_number_column=args.get('uhl_system_number_column', 'uhl_system_number'),
            nhs_number_column=args.get('nhs_number_column', 'nhs_number'),
            family_name_column=args.get('family_name_column', 'family_name'),
            given_name_column=args.get('given_name_column', 'given_name'),
            gender_column=args.get('gender_column', 'gender'),
            dob_column=args.get('dob_column', 'dob'),
            postcode_column=args.get('postcode_column', 'postcode'),
        )

        args.set_params_with_object(params, 'demographics_request', creator=self.faker.demographics_request())

        return self.cls(**params)


class DemographicsRequestDataCreator(FakeCreator):
    @property
    def cls(self):
        return DemographicsRequestData

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            row_number=args.get('row_number', self.faker.unique.pyint()),
            nhs_number=args.get('nhs_number', self.faker.unique.nhs_number()),
            uhl_system_number=args.get('uhl_system_number', self.faker.unique.uhl_system_number()),
            family_name=args.get('family_name', self.faker.last_name()),
            given_name=args.get('given_name', self.faker.first_name()),
            gender=args.get('gender', choice(['f', 'm'])),
            dob=args.get('dob', self.faker.date_object()),
            postcode=args.get('postcode', self.faker.postcode()),
        )

        args.set_params_with_object(params, 'demographics_request', creator=self.faker.demographics_request())

        return self.cls(**params)


class DemographicsRequestPmiDataCreator(FakeCreator):
    @property
    def cls(self):
        return DemographicsRequestPmiData

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            nhs_number=args.get('nhs_number', self.faker.unique.nhs_number()),
            uhl_system_number=args.get('uhl_system_number', self.faker.unique.uhl_system_number()),
            family_name=args.get('family_name', self.faker.last_name()),
            given_name=args.get('given_name', self.faker.first_name()),
            gender=args.get('gender', choice(['f', 'm'])),
            date_of_birth=args.get('date_of_birth', self.faker.date_object()),
            date_of_death=args.get('date_of_death', self.faker.date_object()),
            postcode=args.get('postcode', self.faker.postcode()),
        )

        args.set_params_with_object(params, 'demographics_request_data', creator=self.faker.demographics_request_data())

        return self.cls(**params)


class DemographicsProvider(BaseProvider):
    @cache
    def demographics_request(self):
        return DemographicsRequestCreator(self)

    @cache
    def demographics_request_column(self):
        return DemographicsRequestColumnCreator(self)

    @cache
    def demographics_request_column_definition(self):
        return DemographicsRequestColumnDefinitionCreator(self)

    @cache
    def demographics_request_data(self):
        return DemographicsRequestDataCreator(self)

    @cache
    def demographics_request_pmi_data(self):
        return DemographicsRequestPmiDataCreator(self)
