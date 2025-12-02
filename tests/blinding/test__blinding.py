
from identity.model.id import PseudoRandomId
from identity.model.blinding import Blinding
from lbrc_flask.pytest.helpers import login
from lbrc_flask.database import db
from sqlalchemy import select


def _test_blinding(client, faker, study, expected_blinding_types):
    u = login(client, faker)

    ids = study.get_blind_ids('hello', u)

    db.session.add_all(ids)
    db.session.commit()

    _assert_ids_created_correctly('hello', ids, expected_blinding_types)


def _assert_ids_created_correctly(unblind_id, ids, blinding_types):
    assert len(ids) == len(blinding_types)
    assert Blinding.query.count() == len(blinding_types)
    assert PseudoRandomId.query.count() == len(blinding_types)
    assert sorted(blinding_types) == sorted([i.blinding_type for i in ids])

    for id in ids:
        assert id.unblind_id == unblind_id

        prid = PseudoRandomId.query.filter_by(
            pseudo_random_id_provider_id = id.blinding_type.pseudo_random_id_provider_id,
            full_code = id.pseudo_random_id.full_code,
        ).one()

        assert prid is not None

        assert Blinding.query.filter_by(
            blinding_type_id = id.blinding_type_id,
            unblind_id = unblind_id,
            pseudo_random_id_id = prid.id,
        ).count() == 1


def test__get_blind_ids___no_types(client, faker):
    _test_blinding(client, faker, faker.get_test_study(), [])


def test__get_blind_ids___one_type(client, faker):
    bt = faker.get_test_blinding_type()

    _test_blinding(client, faker, bt.study, [bt])


def test__get_blind_ids___two_types(client, faker):
    s = faker.get_test_study()

    bts = [
        faker.get_test_blinding_type(study=s),
        faker.get_test_blinding_type(study=s),
    ]

    _test_blinding(client, faker, s, bts)


def test__get_blind_ids___type_deleted(client, faker):
    s = faker.get_test_study()

    bts = [
        faker.get_test_blinding_type(study=s),
        faker.get_test_blinding_type(study=s),
    ]

    bt_deleted = faker.get_test_blinding_type(
        study=s,
        deleted=True,
    )

    _test_blinding(client, faker, s, bts)
