# -*- coding: utf-8 -*-

import io
import csv
import pytest
from faker import Faker
from faker.providers import BaseProvider
from identity.model import User
from openpyxl import Workbook


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


@pytest.yield_fixture(scope="function")
def faker():
    result = Faker("en_GB")
    result.add_provider(FakerProvider)
    result.add_provider(FakerProviderCsv)
    result.add_provider(FakerProviderXslx)

    yield result
