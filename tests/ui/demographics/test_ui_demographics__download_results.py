import pytest
from datetime import datetime
from flask import url_for
from identity.demographics.model import DemographicsRequest
from lbrc_flask.database import db
from lbrc_flask.pytest.helpers import login, logout
from tests.demographics import (
    do_create_request,
    do_define_columns_post,
    do_submit,
)
from lbrc_flask.pytest.asserts import assert__requires_login
from tests.ui.demographics import RESULT_CREATED, _assert_uploaded_file_on_index, _remove_files


def _url(external=True, **kwargs):
    return url_for('ui.demographics_download_result', _external=external, **kwargs)


@pytest.mark.skip(reason="Flask_Login is adding extra parameters to URL")
def test__get__requires_login(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    logout(client)

    assert__requires_login(client, _url(id=dr.id, external=False))


def test__ui_demographics_no_result_created(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    response = do_submit(client, dr.id)

    response = client.get(url_for('ui.demographics_download_result', id=dr.id, _external=True))
    assert response.status_code == 404

    _remove_files(dr)


def test__ui_demographics_result_created__download(client, faker):
    user = login(client, faker)

    dr = do_create_request(client, faker, user)
    do_define_columns_post(client, dr.id, dr.columns[0], dr.columns[1], dr.columns[2], dr.columns[3], dr.columns[4], dr.columns[5], dr.columns[6])

    response = do_submit(client, dr.id)

    dr.result_created_datetime = datetime.utcnow()

    db.session.add(dr)
    db.session.commit()

    contents = faker.text()

    with open(dr.result_filepath, "w") as f:
        f.write(contents)
        
    _assert_uploaded_file_on_index(client, dr.filename, dr.id, RESULT_CREATED)

    response = client.get(url_for('ui.demographics_download_result', id=dr.id, _external=True))
    assert response.status_code == 200
    assert response.get_data().decode("utf8") == contents

    dr = DemographicsRequest.query.get(dr.id)
    assert dr.result_downloaded_datetime is not None
    assert dr.result_downloaded == True

    # Do not allows others to download
    logout(client)

    user = login(client, faker)
    response = client.get(url_for('ui.demographics_download_result', id=dr.id, _external=True))
    assert response.status_code == 403

    _remove_files(dr)
