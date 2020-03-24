# -*- coding: utf-8 -*-

import io
import csv
import pytest
import datetime
from faker import Faker
from faker.providers import BaseProvider
from identity.model import User
from openpyxl import Workbook
from random import randint, choice
from identity.validators import (
    is_invalid_nhs_number,
    calculate_nhs_number_checksum,
)

class FakerProvider(BaseProvider):
    def column_headers(self, columns):
        return ['X' * i for i in range(1, columns)]

    def user_details(self):
        u = User(
            first_name=self.generator.first_name(),
            last_name=self.generator.last_name(),
            username=self.generator.email(),
            active=True,
        )
        return u

    def nhs_number(self):
        while True:  
            number = randint(100_000_000, 999_999_999)
            whole_num = f'{number}{calculate_nhs_number_checksum(number)}'

            if(not is_invalid_nhs_number(whole_num)):  
                return whole_num

    def uhl_system_number(self):
        prefix = choice['S', 'R', 'F', 'G', 'U', 'LB', 'RTD']
        return f'{prefix}{randint(1_000_000, 9_999_999)}'

    def person_details(self):
        if not randint(0, 1):
            return self.female_person_details()
        else:
            return self.male_person_details()

    def female_person_details(self):
        return {**{
            'family_name': self.generator.last_name_female(),
            'given_name': self.generator.first_name_female(),
            'gender': 'F',
        }, **self._generic_person_details()}

    def male_person_details(self):
        return {**{
            'family_name': self.generator.last_name_male(),
            'given_name': self.generator.first_name_male(),
            'gender': 'M',
        }, **self._generic_person_details()}

    def _generic_person_details(self):
        dob = self.generator.date_between(start_date='-80y', end_date='-30y')

        if randint(0, 10):
            dod = ''
        else:
            dod = self.generator.date_between(start_date=dob, end_date='today')

        return {
            'dob': dob,
            'date_of_death': dod,
        }


class FakerProviderCsv(BaseProvider):
    def csv_string(self, headers, data=None, rows=10):

        csf_file = io.StringIO()
        writer = csv.DictWriter(csf_file, fieldnames=headers)

        writer.writeheader()

        if data is None:
            for _ in range(rows):
                writer.writerow(dict(zip(headers, self.generator.pylist(len(headers), False, 'str'))))
        else:
            for d in data:
                writer.writerow(dict(zip(headers, d)))

        return csf_file.getvalue()


class FakerProviderXslx(BaseProvider):
    def xslx_data(self, headers, data=None, rows=10):

        wb = Workbook()
        ws1 = wb.active

        ws1.append(headers)

        if data is None:
            for _ in range(rows):
                ws1.append(self.generator.pylist(len(headers), False, 'str'))
        else:
            for d in data:
                ws1.append(d)

        result = io.BytesIO()
        wb.save(result)

        return result.getvalue()


class FakerProviderPmi(BaseProvider):

    def __init__(self, generator):
        super().__init__(generator)

        self._details = {}

    
    def pmi_details(self, key):
        if not key in self._details:
            self._details[key] = self.create_pmi_details()
        
        return self._details[key]

    def create_pmi_details(self):
        f = FakerProvider(self.generator)
        return {**f.person_details, **{
            'nhs_number': f.nhs_number(),
            'uhl_system_number': f.uhl_system_number(),
            'postcode': self.generator.postcode(),
        }}


@pytest.yield_fixture(scope="function")
def faker():
    result = Faker("en_GB")
    result.add_provider(FakerProvider)
    result.add_provider(FakerProviderCsv)
    result.add_provider(FakerProviderXslx)
    result.add_provider(FakerProviderPmi)

    yield result
