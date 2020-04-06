# -*- coding: utf-8 -*-

import pytest
import re
from flask import url_for
from tests import login, add_all_studies
from identity.printing.briccs import (
    ID_NAME_BRICCS_PARTICIPANT,
    ID_NAME_BRICCS_SAMPLE,
    ID_NAME_BRICCS_ALIQUOT,
)
from identity.model.security import User
from identity.model import Study
from identity.blinding.model import (
    BlindingSet,
    Blinding,
)
from identity.database import db


@pytest.mark.parametrize(
    "blinding_set_name",
    [
        ('DisA'),
        ('SCAD'),
    ],
)
def test__ui_blinding_blinding(client, faker, blinding_set_name):
    user = login(client, faker)
    add_all_studies(user)

    blinding_set = BlindingSet.query.filter_by(name=blinding_set_name).first()

    resp = client.post(url_for('ui.blinding', id=blinding_set.study.id, _external=True), data=dict(
        id='hello',
        blinding_set_id=blinding_set.id
    ), follow_redirects=True)

    assert resp.status_code == 200

    for bt in blinding_set.blinding_types:
        assert (
            Blinding.query
            .filter_by(blinding_type_id=bt.id)
            .filter_by(unblind_id='hello')
            .count()
        ) == 1

        b = (
            Blinding.query
            .filter_by(blinding_type_id=bt.id)
            .filter_by(unblind_id='hello')
            .first()
        )

        assert b is not None

        dt = resp.soup.find("dt", string=bt.name)
        assert dt is not None
        dd = dt.find_next_sibling("dd")
        assert dd.string == b.pseudo_random_id.full_code


@pytest.mark.parametrize(
    "blinding_set_name",
    [
        ('DisA'),
        ('SCAD'),
    ],
)
def test__ui_blinding_existing(client, faker, blinding_set_name):
    user = login(client, faker)
    add_all_studies(user)

    blinding_set = BlindingSet.query.filter_by(name=blinding_set_name).first()

    resp = client.post(url_for('ui.blinding', id=blinding_set.study.id, _external=True), data=dict(
        id='hello',
        blinding_set_id=blinding_set.id
    ), follow_redirects=True)

    assert resp.status_code == 200

    existing = {}

    for bt in blinding_set.blinding_types:
        assert (
            Blinding.query
            .filter_by(blinding_type_id=bt.id)
            .filter_by(unblind_id='hello')
            .count()
        ) == 1

        b = (
            Blinding.query
            .filter_by(blinding_type_id=bt.id)
            .filter_by(unblind_id='hello')
            .first()
        )

        existing[bt.name] = b.pseudo_random_id.full_code

    resp = client.post(url_for('ui.blinding', id=blinding_set.study.id, _external=True), data=dict(
        id='hello',
        blinding_set_id=blinding_set.id
    ), follow_redirects=True)

    assert resp.status_code == 200

    for bt in blinding_set.blinding_types:
        assert (
            Blinding.query
            .filter_by(blinding_type_id=bt.id)
            .filter_by(unblind_id='hello')
            .count()
        ) == 1

    for bt, b in existing.items():
        dt = resp.soup.find("dt", string=bt)
        assert dt is not None
        dd = dt.find_next_sibling("dd")
        assert dd.string == b


@pytest.mark.parametrize(
    "blinding_set_name",
    [
        ('DisA'),
        ('SCAD'),
    ],
)
def test__ui_unblinding_existing(client, faker, blinding_set_name):
    user = login(client, faker)
    add_all_studies(user)

    blinding_set = BlindingSet.query.filter_by(name=blinding_set_name).first()

    resp = client.post(url_for('ui.blinding', id=blinding_set.study.id, _external=True), data=dict(
        id='hello',
        blinding_set_id=blinding_set.id
    ))

    assert resp.status_code == 302

    existing = []

    for bt in blinding_set.blinding_types:
        assert (
            Blinding.query
            .filter_by(blinding_type_id=bt.id)
            .filter_by(unblind_id='hello')
            .count()
        ) == 1

        b = (
            Blinding.query
            .filter_by(blinding_type_id=bt.id)
            .filter_by(unblind_id='hello')
            .first()
        )

        existing.append(b.pseudo_random_id.full_code)

    for id in existing:
        resp = client.post(url_for('ui.unblinding', id=blinding_set.study.id, _external=True), data=dict(
            id=id,
            blinding_set_id=blinding_set.id
        ))

        assert resp.status_code == 302

        resp.soup.find("h3", string=re.compile('hello'))


@pytest.mark.parametrize(
    "blinding_set_name, allowed",
    [
        ('DisA', False),
        ('SCAD', True),
    ],
)
def test__ui_blinding_permission(client, faker, blinding_set_name, allowed):
    user = login(client, faker)

    user.studies.add(Study.query.filter_by(name="SCAD").first())
    db.session.commit()

    blinding_set = BlindingSet.query.filter_by(name=blinding_set_name).first()

    resp = client.post(url_for('ui.blinding', id=blinding_set.study.id, _external=True), data=dict(
        id='hello',
        blinding_set_id=blinding_set.id
    ), follow_redirects=True)

    if allowed:
        assert resp.status_code == 200
    else:
        assert resp.status_code == 403


@pytest.mark.parametrize(
    "blinding_set_name, allowed",
    [
        ('DisA', False),
        ('SCAD', True),
    ],
)
def test__ui_unblinding_permission(client, faker, blinding_set_name, allowed):
    user = login(client, faker)

    user.studies.add(Study.query.filter_by(name="SCAD").first())
    db.session.commit()

    blinding_set = BlindingSet.query.filter_by(name=blinding_set_name).first()

    resp = client.post(
        url_for('ui.unblinding', id=blinding_set.study.id, _external=True),
        data=dict(id='hello'),
        follow_redirects=True,
    )

    if allowed:
        assert resp.status_code == 200
    else:
        assert resp.status_code == 403
