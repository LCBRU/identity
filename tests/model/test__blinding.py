from identity.model.id import PseudoRandomId
from identity.model.blinding import Blinding
from lbrc_flask.pytest.helpers import login
from lbrc_flask.database import db
from sqlalchemy import select, func

from identity.services.blinding import get_study_blinding_ids


def _test_blinding(client, faker, study, expected_blinding_types):
    u = login(client, faker)

    ids = get_study_blinding_ids(study, 'hello')
    db.session.add_all(ids)
    db.session.commit()

    _assert_ids_created_correctly('hello', ids, expected_blinding_types)


def _assert_ids_created_correctly(unblind_id, ids, blinding_types):
    assert len(ids) == len(blinding_types)
    assert db.session.execute(select(func.count(1)).select_from(Blinding)).scalar() == len(blinding_types)
    assert db.session.execute(select(func.count(1)).select_from(PseudoRandomId)).scalar() == len(blinding_types)
    assert sorted(blinding_types) == sorted([i.blinding_type for i in ids])

    for id in ids:
        assert id.unblind_id == unblind_id

        prid = db.session.execute(
            select(PseudoRandomId)
            .where(PseudoRandomId.pseudo_random_id_provider_id == id.blinding_type.pseudo_random_id_provider_id)
            .where(PseudoRandomId.full_code == id.pseudo_random_id.full_code)
        ).scalar_one()

        assert prid is not None

        assert db.session.execute(
            select(func.count(1))
            .where(Blinding.blinding_type_id == id.blinding_type_id)
            .where(Blinding.unblind_id == unblind_id)
            .where(Blinding.pseudo_random_id_id == prid.id)
        ).scalar_one() == 1


def test__get_blind_ids___no_types(client, faker):
    _test_blinding(client, faker, faker.study().get(save=True), [])


def test__get_blind_ids___one_type(client, faker):
    bt = faker.blinding_type().get(save=True)

    _test_blinding(client, faker, bt.study, [bt])


def test__get_blind_ids___two_types(client, faker):
    s = faker.study().get(save=True)

    bts = [
        faker.blinding_type().get(save=True, study=s),
        faker.blinding_type().get(save=True, study=s),
    ]

    _test_blinding(client, faker, s, bts)


def test__get_blind_ids___type_deleted(client, faker):
    s = faker.study().get(save=True)

    bts = [
        faker.blinding_type().get(save=True, study=s),
        faker.blinding_type().get(save=True, study=s),
    ]

    bt_deleted = faker.blinding_type().get(save=True, study=s, deleted=True)

    _test_blinding(client, faker, s, bts)
