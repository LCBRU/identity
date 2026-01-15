import contextlib
import os
import re
from flask import url_for

AWAITING_DEFINE_COLUMNS = 'AWAITING_DEFINE_COLUMNS'
AWAITING_SUBMISSION = 'AWAITING_SUBMISSION'
AWAITING_COMPLETION = 'AWAITING_COMPLETION'
RESULT_CREATED = 'RESULT_CREATED'


def _assert_uploaded_file_on_index(client, filename, id, status):
    response = client.get(url_for('ui.demographics'))
    soup = response.soup

    assert soup.find(string=re.compile(filename)) is not None

    print(soup.prettify())

    url_define_columns = url_for('ui.demographics_define_columns', id=id)
    a_define_columns = soup.select(f'a[hx-get="{url_define_columns}"]')

    url_submit = url_for('ui.demographics_submit', id=id)
    a_submit = soup.select(f'a[hx-get="{url_submit}"]')

    url_delete = url_for('ui.demographics_delete', id=id)
    a_delete = soup.select(f'a[hx-post="{url_delete}"]')

    url_download = url_for('ui.demographics_download_result', id=id)
    a_download = soup.select(f'a[href="{url_download}"]')

    if status == AWAITING_DEFINE_COLUMNS:
        assert len(a_define_columns) == 1
        assert len(a_submit) == 0
        assert len(a_delete) == 1
        assert len(a_download) == 0
    elif status == AWAITING_SUBMISSION:
        assert len(a_define_columns) == 1
        assert len(a_submit) == 1
        assert len(a_delete) == 1
        assert len(a_download) == 0
    elif status == AWAITING_COMPLETION:
        assert len(a_define_columns) == 0
        assert len(a_submit) == 0
        assert len(a_delete) == 1
        assert len(a_download) == 0
    elif status == RESULT_CREATED:
        assert len(a_define_columns) == 0
        assert len(a_submit) == 0
        assert len(a_delete) == 1
        assert len(a_download) == 1


def _assert_file_not_on_index(client, filename):
    response = client.get(url_for('ui.demographics'))

    assert response.soup.find('h1', string=filename) is None


def _remove_files(dr):
    with contextlib.suppress(FileNotFoundError):
        os.remove(dr.filepath)
        os.remove(dr.result_filepath)
