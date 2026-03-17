from functools import cache
from identity.printing import LabelBundle
from identity.model.id import PseudoRandomId, PseudoRandomIdProvider
from identity.model.blinding import Blinding, BlindingType
from identity.model.security import User
import io
import csv
from faker.providers import BaseProvider
from openpyxl import Workbook
from identity.services.pmi import PmiData
from identity.model import Study
from identity.api.model import ApiKey
from lbrc_flask.pytest.faker import UserCreator as BaseUserCreator, FakeCreator, FakeCreatorArgs


class UserCreator(BaseUserCreator):
    cls = User


class ApiKeyCreator(FakeCreator):
    @property
    def cls(self):
        return ApiKey

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            user = args.get('user', self.faker.user().get(save=save)),
        )

        return self.cls(**params)


class StudyCreator(FakeCreator):
    @property
    def cls(self):
        return Study

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            name = args.get('name', self.faker.pystr(min_chars=5, max_chars=100)),
        )

        result: Study = self.cls(**params)

        if 'owner' in args:
            result.users.append(args.get('owner'))

        return result


class PseudoRandomIdProviderCreator(FakeCreator):
    @property
    def cls(self):
        return PseudoRandomIdProvider

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            name = args.get('name', self.faker.pystr(min_chars=5, max_chars=100)),
            prefix = args.get('prefix', self.faker.pystr(min_chars=3, max_chars=3).upper()),
        )

        return self.cls(**params)


class PseudoRandomIdCreator(FakeCreator):
    @property
    def cls(self):
        return PseudoRandomId

    def _create_item(self, save, args: FakeCreatorArgs):
        provider: PseudoRandomIdProvider = args.get('pseudo_random_id_provider', self.faker.pseudo_random_id_provider().get(save=True))

        return provider.allocate_id()


class BlindingTypeCreator(FakeCreator):
    @property
    def cls(self):
        return BlindingType

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            name = args.get('name', self.faker.pystr(min_chars=5, max_chars=100)),
            deleted = args.get('deleted', False),
        )

        args.set_params_with_object(params, 'study', creator=self.faker.study())
        args.set_params_with_object(params, 'pseudo_random_id_provider', creator=self.faker.pseudo_random_id_provider())
            
        return self.cls(**params)


class BlindingCreator(FakeCreator):
    @property
    def cls(self):
        return Blinding

    def _create_item(self, save, args: FakeCreatorArgs):
        owner = args.get('owner', self.faker.user().get(save=True))
        blinding_type: BlindingType = args.get('blinding_type', self.faker.blinding_type().get(save=True, study=self.faker.study().get(save=True, owner=owner)))

        return blinding_type.get_blind_id(
            unblind_id=args.get('unblind_id', self.faker.pystr(min_chars=5, max_chars=100)),
            user=owner,
        )


class LabelBundleCreator(FakeCreator):
    @property
    def cls(self):
        return LabelBundle

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            name = args.get('name', self.faker.pystr(min_chars=5, max_chars=100)),
            disable_batch_printing=self.faker.pybool(),
            user_defined_participant_id=self.faker.pybool(),
        )

        args.set_params_with_object(params, 'study', creator=self.faker.study())

        return self.cls(**params)


class PmiDataCreator(FakeCreator):
    @property
    def cls(self):
        return PmiData

    def _create_item(self, save, args: FakeCreatorArgs):

        dets = self._create_pmi_details()

        result = PmiData(
            nhs_number=dets.get('nhs_number'),
            uhl_system_number=dets.get('uhl_system_number'),
            family_name=dets.get('family_name'),
            given_name=dets.get('given_name'),
            gender=dets.get('gender'),
            date_of_birth=dets.get('date_of_birth'),
            date_of_death=dets.get('date_of_death'),
            postcode=dets.get('postcode'),
            mapping=dets,
        )

        return result

    def _create_pmi_details(self) -> dict:
        return {key: value for key, value in self.faker.person_details().items() if key in PmiData._fields}


class IdentityProvider(BaseProvider):
    @cache
    def user(self):
        return UserCreator(self)

    @cache
    def api_key(self):
        return ApiKeyCreator(self)

    @cache
    def study(self):
        return StudyCreator(self)

    @cache
    def pseudo_random_id_provider(self):
        return PseudoRandomIdProviderCreator(self)
    
    @cache
    def pseudo_random_id(self):
        return PseudoRandomIdCreator(self)
    
    @cache
    def blinding_type(self):
        return BlindingTypeCreator(self)

    @cache
    def blinding(self):
        return BlindingCreator(self)

    @cache
    def label_bundle(self):
        return LabelBundleCreator(self)
    
    @cache
    def pmi_data(self):
        return PmiDataCreator(self)
    
    def column_headers(self, columns):
        return ['X' * i for i in range(1, columns)]

    def csv_string(self, headers, data=None, rows=10):

        csf_file = io.StringIO()
        writer = csv.DictWriter(csf_file, fieldnames=headers)

        writer.writeheader()

        if data is None:
            for _ in range(rows):
                writer.writerow(dict(zip(headers, self.generator.pylist(len(headers), False, ['str']))))
        else:
            for d in data:
                writer.writerow(dict(zip(headers, d)))

        return csf_file.getvalue()

    def xslx_data(self, headers, data=None, rows=10):

        wb = Workbook()
        ws1 = wb.active

        ws1.append(headers)

        if data is None:
            for _ in range(rows):
                ws1.append(self.generator.pylist(len(headers), False, ['str']))
        else:
            for d in data:
                ws1.append(d)

        result = io.BytesIO()
        wb.save(result)

        return result.getvalue()
