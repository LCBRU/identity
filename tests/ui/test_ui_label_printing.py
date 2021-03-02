import pytest
from flask import url_for
from identity.printing.model import LabelPack
from identity.printing.cardiomet import ID_TYPE_PARTICIPANT as CARDIOMET_ID_TYPE_PARTICIPANT
from identity.printing.go_dcm import ID_TYPE_PARTICIPANT as GO_DCM_ID_TYPE_PARTICIPANT
from identity.model.id import PseudoRandomId, PseudoRandomIdProvider
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__requires_login, assert__redirect


def _url(external=True, **kwargs):
    return url_for('ui.label_print', _external=external, **kwargs)


def test__get__requires_login(client):
    pack = LabelPack.query.filter_by(type='CardiometPack').one()

    assert__requires_login(client, _url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
        external=False,
    ))


@pytest.mark.parametrize(
    "pack_count",
    [
        (1),
        (10),
        (50),
    ],
)
def test__label_print__no_id_entry__study_redirect(client, faker, pack_count):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='CardiometPack').one()

    resp = client.get(_url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=pack_count,
    ))

    assert__redirect(resp, 'ui.study', id=pack.study_id)

    assert PseudoRandomId.query.join(PseudoRandomIdProvider).filter_by(prefix=CARDIOMET_ID_TYPE_PARTICIPANT).count() == pack_count


@pytest.mark.parametrize(
    "pack_count",
    [
        (1),
        (10),
        (50),
    ],
)
def test__label_print__no_id_entry__labels_redirect(client, faker, pack_count):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='CardiometPack').one()

    resp = client.get(_url(
        referrer='labels',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=pack_count,
    ))

    assert__redirect(resp, 'ui.labels')

    assert PseudoRandomId.query.join(PseudoRandomIdProvider).filter_by(prefix=CARDIOMET_ID_TYPE_PARTICIPANT).count() == pack_count


def test__label_print__requires_id_entry(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    resp = client.get(_url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
    ))

    assert__redirect(
        resp,
        'ui.label_print_definition',
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
    )

    assert PseudoRandomId.query.join(PseudoRandomIdProvider).filter_by(prefix=GO_DCM_ID_TYPE_PARTICIPANT).count() == 0


def test__label_print__not_a_user_study(client, faker):
    user = login(client, faker)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    resp = client.get(_url(
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
    ))

    assert resp.status_code == 403
