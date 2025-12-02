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

    assert response.soup.find(string=re.compile(filename)) is not None

    if status == AWAITING_DEFINE_COLUMNS:
        assert response.soup.find('a', attrs={"hx-get" : url_for('ui.demographics_define_columns', id=id)}) is not None
        assert response.soup.find('a', attrs={"hx-get" : url_for('ui.demographics_submit', id=id)}) is None
        assert response.soup.find('a', attrs={"hx-post" : url_for('ui.demographics_delete', id=id)}) is not None
    elif status == AWAITING_SUBMISSION:
        assert response.soup.find('a', attrs={"hx-get" : url_for('ui.demographics_define_columns', id=id)}) is not None
        assert response.soup.find('a', attrs={"hx-get" : url_for('ui.demographics_submit', id=id)}) is not None
        assert response.soup.find('a', attrs={"hx-post" : url_for('ui.demographics_delete', id=id)}) is not None
    elif status == AWAITING_COMPLETION:
        assert response.soup.find('a', attrs={"hx-get" : url_for('ui.demographics_define_columns', id=id)}) is None
        assert response.soup.find('a', attrs={"hx-get" : url_for('ui.demographics_submit', id=id)}) is None
        assert response.soup.find('a', attrs={"hx-post" : url_for('ui.demographics_delete', id=id)}) is not None
    elif status == RESULT_CREATED:
        assert response.soup.find('a', attrs={"hx-get" : url_for('ui.demographics_define_columns', id=id)}) is None
        assert response.soup.find('a', attrs={"hx-get" : url_for('ui.demographics_submit', id=id)}) is None
        assert response.soup.find('a', attrs={"hx-post" : url_for('ui.demographics_delete', id=id)}) is not None
        assert response.soup.find('a', href=url_for('ui.demographics_download_result', id=id)) is not None


def _assert_file_not_on_index(client, filename):
    response = client.get(url_for('ui.demographics'))

    assert response.soup.find('h1', string=filename) is None


def _remove_files(dr):
    with contextlib.suppress(FileNotFoundError):
        os.remove(dr.filepath)
        os.remove(dr.result_filepath)
