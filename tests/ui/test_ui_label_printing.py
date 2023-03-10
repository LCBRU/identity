import pytest
from flask import url_for
from identity.model.id import PseudoRandomId, PseudoRandomIdProvider
from lbrc_flask.pytest.helpers import login
from lbrc_flask.pytest.asserts import assert__requires_login, assert__redirect


def _url(external=True, **kwargs):
    return url_for('ui.label_bundle_print', _external=external, **kwargs)


def test__get__requires_login(client, faker):
    bundle = faker.get_test_label_bundle()

    assert__requires_login(client, _url(
        referrer='study',
        study_id=bundle.study_id,
        label_bundle_id=bundle.id,
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
@pytest.mark.skip(reason="Cannot check PseudoRandomId as faker label pack contains no labels")
def test__label_print__no_id_entry__study_redirect(client, faker, pack_count):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()
    user.studies.append(bundle.study)

    resp = client.get(_url(
        referrer='study',
        study_id=bundle.study_id,
        label_bundle_id=bundle.id,
        count=pack_count,
    ))

    assert__redirect(resp, 'ui.study', id=bundle.study_id)

    # Replace prefix with what the actual prefix will be
    assert PseudoRandomId.query.join(PseudoRandomIdProvider).filter_by(prefix='prefix').count() == pack_count


@pytest.mark.parametrize(
    "pack_count",
    [
        (1),
        (10),
        (50),
    ],
)
@pytest.mark.skip(reason="Cannot check PseudoRandomId as faker label pack contains no labels")
def test__label_print__no_id_entry__labels_redirect(client, faker, pack_count):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()
    user.studies.append(bundle.study)

    resp = client.get(_url(
        referrer='labels',
        study_id=bundle.study_id,
        label_bundle_id=bundle.id,
        count=pack_count,
    ))

    assert__redirect(resp, 'ui.labels')

    # Replace prefix with what the actual prefix will be
    assert PseudoRandomId.query.join(PseudoRandomIdProvider).filter_by(prefix='prefix').count() == pack_count


@pytest.mark.skip(reason="Cannot check PseudoRandomId as faker label pack contains no labels")
def test__label_print__requires_id_entry(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()
    user.studies.append(bundle.study)

    resp = client.get(_url(
        referrer='study',
        study_id=bundle.study_id,
        label_bundle_id=bundle.id,
        count=1,
    ))

    assert__redirect(
        resp,
        'ui.label_bundle_definition',
        referrer='study',
        study_id=bundle.study_id,
        label_bundle_id=bundle.id,
        count=1,
    )

    # Replace prefix with what the actual prefix will be
    assert PseudoRandomId.query.join(PseudoRandomIdProvider).filter_by(prefix='prefix').count() == 0


def test__label_print__not_a_user_study(client, faker):
    user = login(client, faker)

    bundle = faker.get_test_label_bundle()

    resp = client.get(_url(
        referrer='study',
        study_id=bundle.study_id,
        label_bundle_id=bundle.id,
        count=1,
    ))

    assert resp.status_code == 403
