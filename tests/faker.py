from identity.printing.model import LabelPack
from identity.model.id import PseudoRandomIdProvider
from identity.blinding.model import Blinding, BlindingSet, BlindingType
from identity.model.security import User
import io
import csv
from faker.providers import BaseProvider
from openpyxl import Workbook
from identity.services.pmi import PmiData
from identity.model import Study
from identity.api.model import ApiKey
from lbrc_flask.database import db


class IdentityProvider(BaseProvider):

    def user_details(self):
        u = User(
            first_name=self.generator.first_name(),
            last_name=self.generator.last_name(),
            email=self.generator.email(),
            active=True,
        )
        return u

    def get_test_user(self,  **kwargs):
        u = self.user_details(**kwargs)

        db.session.add(u)
        db.session.commit()

        return u

    def get_api_key(self):
        u = self.user_details()
        db.session.add(u)

        a = ApiKey()
        a.user = u
        db.session.add(a)

        db.session.commit()

        return a

    def add_all_studies(self, user):
        user.studies.update(Study.query.all())
    
    def column_headers(self, columns):
        return ['X' * i for i in range(1, columns)]

    def study_details(self, name=None, owner=None):
        if name is None:
            name = self.generator.pystr(min_chars=5, max_chars=100)

        result = Study(
            name=name,
        )

        if owner:
            result.users.append(owner)

        return result

    def get_test_study(self,  **kwargs):
        s = self.study_details(**kwargs)

        db.session.add(s)
        db.session.commit()

        return s

    def blinding_set_details(self, name=None, study=None):
        if name is None:
            name = self.generator.pystr(min_chars=5, max_chars=100)
        
        result = BlindingSet(name=name)

        if study is None:
            result.study = self.study_details()
        elif study.id is None:
            result.study = study
        else:
            result.study_id = study.id

        return result

    def get_test_blinding_set(self,  **kwargs):
        bs = self.blinding_set_details(**kwargs)

        db.session.add(bs)
        db.session.commit()

        return bs

    def pseudo_random_id_provider_details(self, name=None, prefix=None):
        if name is None:
            name = self.generator.pystr(min_chars=5, max_chars=100)
        if prefix is None:
            prefix = self.generator.pystr(min_chars=3, max_chars=3).upper()
        
        return PseudoRandomIdProvider(name=name, prefix=prefix)


    def get_test_pseudo_random_id_provider(self,  **kwargs):
        p = self.pseudo_random_id_provider_details(**kwargs)

        db.session.add(p)
        db.session.commit()

        return p

    def blinding_type_details(self, name=None, blinding_set=None, pseudo_random_id_provider=None, deleted=False):
        if name is None:
            name = self.generator.pystr(min_chars=5, max_chars=100)
        
        result = BlindingType(name=name, deleted=deleted)

        if blinding_set is None:
            result.blinding_set = self.blinding_set_details()
        elif blinding_set.id is None:
            result.blinding_set = blinding_set
        else:
            result.blinding_set_id = blinding_set.id

        if pseudo_random_id_provider is None:
            result.pseudo_random_id_provider = self.pseudo_random_id_provider_details()
        elif pseudo_random_id_provider.id is None:
            result.pseudo_random_id_provider = pseudo_random_id_provider
        else:
            result.pseudo_random_id_provider_id = pseudo_random_id_provider.id

        return result


    def get_test_blinding_type(self,  **kwargs):
        bt = self.blinding_type_details(**kwargs)

        db.session.add(bt)
        db.session.commit()

        return bt

    def blinding_details(self, unblind_id=None, blinding_type=None, pseudo_random_id=None):
        if unblind_id is None:
            unblind_id = self.generator.pystr(min_chars=5, max_chars=100)

        result = Blinding(unblind_id=unblind_id)

        if blinding_type is None:
            result.blinding_type = self.blinding_type_details()
        elif blinding_type.id is None:
            result.blinding_type = blinding_type
        else:
            result.blinding_type_id = blinding_type.id

        if pseudo_random_id is None:
            result.pseudo_random_id = self.pseudo_random_id_details()
        elif pseudo_random_id.id is None:
            result.pseudo_random_id = pseudo_random_id
        else:
            result.pseudo_random_id_id = pseudo_random_id.id

        return result

    def get_test_blinding(self, **kwargs):
        b = self.blinding_details(**kwargs)

        db.session.add(b)
        db.session.commit()

        return b

    def get_test_blinding_with_owner(self, owner, unblind_id=None, **kwargs):
        if unblind_id is None:
            unblind_id = self.generator.pystr(min_chars=5, max_chars=100)

        s = self.get_test_study(owner=owner)
        bs = self.get_test_blinding_set(study=s)
        bt = self.get_test_blinding_type(blinding_set=bs)
        b = bt.get_blind_id(unblind_id, owner)

        db.session.add(b)
        db.session.commit()

        return b

    def label_pack_details(self, type=None, study=None):
        if type is None:
            type = 'Pack'

        result = LabelPack(type=type)

        if study is None:
            result.study = self.study_details()
        elif study.id is None:
            result.study = study
        else:
            result.study_id = study.id

        return result

    def get_test_label_pack(self, **kwargs):
        lp = self.label_pack_details(**kwargs)

        db.session.add(lp)
        db.session.commit()

        return lp


class DemographicsCsvProvider(BaseProvider):
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


class DemographicsXslxProvider(BaseProvider):
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


class PmiProvider(BaseProvider):

    def __init__(self, generator):
        super().__init__(generator)

        self._details = {}

    
    def pmi_details(self, key):
        if not key in self._details:
            self._details[key] = self.create_pmi_details()
        
        return self._details[key]

    def create_pmi_details(self):
        return {key: value for key, value in self.generator.person_details().items() if key in PmiData._fields}
