import pytest
from flask import url_for
from identity.printing.model import LabelPack
from identity.printing.cardiomet import ID_TYPE_PARTICIPANT as CARDIOMET_ID_TYPE_PARTICIPANT
from identity.printing.go_dcm import ID_TYPE_PARTICIPANT as GO_DCM_ID_TYPE_PARTICIPANT
from identity.model.id import PseudoRandomId, PseudoRandomIdProvider
from lbrc_flask.database import db
from lbrc_flask.pytest.helpers import login


def test__labels(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    resp = client.get(url_for(
        'ui.labels',
        _external=True,
    ))

    assert resp.status_code == 200


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

    resp = client.get(url_for(
        'ui.label_print',
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=pack_count,
        _external=True,
    ))

    assert resp.status_code == 302
    assert resp.location == url_for('ui.study', id=pack.study_id, _external=True)

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

    resp = client.get(url_for(
        'ui.label_print',
        referrer='labels',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=pack_count,
        _external=True,
    ))

    assert resp.status_code == 302
    assert resp.location == url_for('ui.labels', _external=True)

    assert PseudoRandomId.query.join(PseudoRandomIdProvider).filter_by(prefix=CARDIOMET_ID_TYPE_PARTICIPANT).count() == pack_count


def test__label_print__requires_id_entry(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    resp = client.get(url_for(
        'ui.label_print',
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
        _external=True,
    ))

    assert resp.status_code == 302
    assert resp.location == url_for(
        'ui.label_print_definition',
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
        _external=True,
    )

    assert PseudoRandomId.query.join(PseudoRandomIdProvider).filter_by(prefix=GO_DCM_ID_TYPE_PARTICIPANT).count() == 0


def test__label_print__not_a_user_study(client, faker):
    user = login(client, faker)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    resp = client.get(url_for(
        'ui.label_print',
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
        _external=True,
    ))

    assert resp.status_code == 403


def test__label_print_definition__get(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    resp = client.get(url_for(
        'ui.label_print_definition',
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
        _external=True,
    ))

    assert resp.status_code == 200


def test__label_print_definition__not_a_study_user__get(client, faker):
    user = login(client, faker)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    resp = client.get(url_for(
        'ui.label_print_definition',
        referrer='study',
        study_id=pack.study_id,
        pack_name=pack.type,
        count=1,
        _external=True,
    ))

    assert resp.status_code == 403


def test__label_print_definition__post__study_redirect(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    data = {
        'participant_id': 'ABCDEFG'
    }

    resp = client.post(
        url_for(
            'ui.label_print_definition',
            referrer='study',
            study_id=pack.study_id,
            pack_name=pack.type,
            count=1,
            _external=True,
        ),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert resp.status_code == 302
    assert resp.location == url_for('ui.study', id=pack.study_id, _external=True)


def test__label_print_definition__post__labels_redirect(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    data = {
        'participant_id': 'ABCDEFG'
    }

    resp = client.post(
        url_for(
            'ui.label_print_definition',
            referrer='labels',
            study_id=pack.study_id,
            pack_name=pack.type,
            count=1,
            _external=True,
        ),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert resp.status_code == 302
    assert resp.location == url_for('ui.labels', _external=True)


def test__label_print_definition__post__no_id_given(client, faker):
    user = login(client, faker)
    faker.add_all_studies(user)

    pack = LabelPack.query.filter_by(type='GoDcmPack').one()

    data = {
        'participant_id': ''
    }

    resp = client.post(
        url_for(
            'ui.label_print_definition',
            referrer='labels',
            study_id=pack.study_id,
            pack_name=pack.type,
            count=1,
            _external=True,
        ),
        buffered=True,
        content_type="multipart/form-data",
        data=data,
    )

    assert resp.status_code == 200


@pytest.mark.parametrize(
    "pack_name, visible",
    [
        ("ScadPack", True),
        ("ScadBloodOnlyPack", True),
        ("ScadFamilyPack", True),
        ("MermaidPack", True),
        ("BriccsPack", False),
    ],
)
def test__ui_buttons_visible(client, faker, pack_name, visible):
    user = login(client, faker)

    pack = LabelPack.query.filter_by(type=pack_name).one()

    if visible:
        user.studies.add(pack.study)
        db.session.commit()

    resp = client.get(url_for('ui.labels', _external=True))

    assert resp.status_code == 200

    assert (resp.soup.find("a", href=url_for('ui.label_print', referrer='labels', pack_name=pack_name, study_id=pack.study_id, count=1)) is not None) == visible
