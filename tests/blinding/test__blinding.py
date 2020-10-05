
from sys import prefix
from identity.ui.views.study import study
from identity.model.id import PseudoRandomId, PseudoRandomIdProvider
from identity.blinding.model import Blinding, BlindingSet, BlindingType
from tests import login
from identity.model import Study
from identity.database import db


def test__get_blind_ids___no_sets(client, faker):
    u = login(client, faker)
    s = Study(name='Fred')

    db.session.add(s)
    db.session.commit()

    ids = s.get_blind_ids('hello', u)

    db.session.commit()

    assert len(ids) == 0
    assert Blinding.query.count() == 0
    assert PseudoRandomId.query.count() == 0


def test__get_blind_ids___sets_no_types(client, faker):
    u = login(client, faker)
    s = Study(name='Fred')
    db.session.add_all([s, BlindingSet(name='A', study=s), BlindingSet(name='B', study=s)])

    db.session.commit()

    ids = s.get_blind_ids('hello', u)

    db.session.commit()

    assert len(ids) == 0
    assert Blinding.query.count() == 0
    assert PseudoRandomId.query.count() == 0


def test__get_blind_ids___one_type(client, faker):
    unblind_id = 'hello'

    u = login(client, faker)
    s = Study(name='Fred')
    bs = BlindingSet(name='A', study=s)
    prp = PseudoRandomIdProvider(name='PS', prefix='PS')
    bts = [BlindingType(name='BT', blinding_set=bs, pseudo_random_id_provider=prp)]

    db.session.add_all([s, bs, *bts])

    db.session.commit()

    ids = s.get_blind_ids(unblind_id, u)

    db.session.commit()

    _assert_ids_created_correctly(unblind_id, ids, bts)


def test__get_blind_ids___two_types__one_set(client, faker):
    unblind_id = 'hello'

    u = login(client, faker)
    s = Study(name='Fred')
    bs = BlindingSet(name='A', study=s)
    prp1 = PseudoRandomIdProvider(name='PS1', prefix='PS1')
    prp2 = PseudoRandomIdProvider(name='PS2', prefix='PS2')

    bts = [
        BlindingType(name='BT1', blinding_set=bs, pseudo_random_id_provider=prp1),
        BlindingType(name='BT2', blinding_set=bs, pseudo_random_id_provider=prp2),
    ]

    db.session.add_all([s, bs, *bts])

    db.session.commit()

    ids = s.get_blind_ids(unblind_id, u)

    db.session.commit()

    _assert_ids_created_correctly(unblind_id, ids, bts)


def test__get_blind_ids___two_sets__one_type_each(client, faker):
    unblind_id = 'hello'

    u = login(client, faker)
    s = Study(name='Fred')
    bss = [
        BlindingSet(name='A', study=s),
        BlindingSet(name='B', study=s),
    ]

    prp1 = PseudoRandomIdProvider(name='PS1', prefix='PS1')
    prp2 = PseudoRandomIdProvider(name='PS2', prefix='PS2')

    bts = [
        BlindingType(name='BT1', blinding_set=bss[0], pseudo_random_id_provider=prp1),
        BlindingType(name='BT2', blinding_set=bss[1], pseudo_random_id_provider=prp2),
    ]

    db.session.add_all([s, *bss, *bts])

    db.session.commit()

    ids = s.get_blind_ids(unblind_id, u)

    db.session.commit()

    _assert_ids_created_correctly(unblind_id, ids, bts)


def test__get_blind_ids___type_deleted(client, faker):
    unblind_id = 'hello'

    u = login(client, faker)
    s = Study(name='Fred')
    bss = [
        BlindingSet(name='A', study=s),
        BlindingSet(name='B', study=s),
    ]

    prp1 = PseudoRandomIdProvider(name='PS1', prefix='PS1')
    prp2 = PseudoRandomIdProvider(name='PS2', prefix='PS2')
    prp3 = PseudoRandomIdProvider(name='PS3', prefix='PS3')

    bts = [
        BlindingType(name='BT1', blinding_set=bss[0], pseudo_random_id_provider=prp1),
        BlindingType(name='BT2', blinding_set=bss[1], pseudo_random_id_provider=prp2),
    ]

    bt_deleted = BlindingType(
        name='BT_Deleted',
        blinding_set=bss[0],
        pseudo_random_id_provider=prp3,
        deleted=True,
    )

    db.session.add_all([s, bt_deleted, *bss, *bts])

    db.session.commit()

    ids = s.get_blind_ids(unblind_id, u)

    db.session.commit()

    _assert_ids_created_correctly(unblind_id, ids, bts)


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
