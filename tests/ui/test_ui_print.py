# -*- coding: utf-8 -*-

import pytest
import datetime
from flask import url_for
from tests import login, add_all_studies
from identity.printing.briccs import (
    ID_NAME_BRICCS_PARTICIPANT,
    ID_NAME_BRICCS_SAMPLE,
    ID_NAME_BRICCS_ALIQUOT,
)
from identity.model import (
    SequentialIdProvider,
    LegacyIdProvider,
    BioresourceIdProvider,
    PseudoRandomIdProvider,
    PseudoRandomId,
    User,
    LegacyId,
    BioresourceId,
)
from identity.printing.model import (
    LabelPack,
)


@pytest.mark.parametrize(
    "pack_name, samples_per_participant, set_count",
    [
        # ("MermaidPack", 10, 1),
        # ("MermaidPack", 10, 10),
        ("BriccsPack", 8, 1),
        ("BriccsPack", 8, 10),
        ("BriccsKetteringPack", 3, 1),
        ("BriccsKetteringPack", 3, 10),
    ],
)
def test__ui_print_briccs_packs(client, faker, pack_name, set_count, samples_per_participant):
    user = login(client, faker)
    add_all_studies(user)

    pack = LabelPack.query.filter_by(type=pack_name).one()

    before = datetime.datetime.utcnow()

    resp = client.get(url_for('ui.label_print', study_id=pack.study_id, referrer='', set=pack_name, count=set_count, _external=True))

    after = datetime.datetime.utcnow()

    assert resp.status_code == 302
    assert resp.location == url_for('ui.labels', _external=True)

    participant_provider_name = ID_NAME_BRICCS_PARTICIPANT
    sample_provider_name = ID_NAME_BRICCS_SAMPLE

    bpt_provider = LegacyIdProvider.query.filter_by(name=participant_provider_name).first()
    bsa_provider = LegacyIdProvider.query.filter_by(name=sample_provider_name).first()

    assert (LegacyId.query
            .filter_by(legacy_id_provider_id=bpt_provider.id)
            .filter(LegacyId.last_updated_datetime >= before)
            .filter(LegacyId.last_updated_datetime <= after)
        ).count() == set_count

    assert (LegacyId.query
            .filter_by(legacy_id_provider_id=bsa_provider.id)
            .filter(LegacyId.last_updated_datetime >= before)
            .filter(LegacyId.last_updated_datetime <= after)
        ).count() == set_count * samples_per_participant


@pytest.mark.parametrize(
    "set_count",
    [
        (1),
        (10),
    ],
)
def test__ui_print_briccs_sample_pack(client, faker, set_count):
    user = login(client, faker)
    add_all_studies(user)

    before = datetime.datetime.utcnow()

    resp = client.get(url_for('ui.label_print', set='BriccsSamplePack', count=set_count, _external=True))

    after = datetime.datetime.utcnow()

    assert resp.status_code == 302
    assert resp.location == url_for('ui.labels', _external=True)

    sample_provider_name = ID_NAME_BRICCS_SAMPLE

    bsa_provider = LegacyIdProvider.query.filter_by(name=sample_provider_name).first()

    assert (LegacyId.query
            .filter_by(legacy_id_provider_id=bsa_provider.id)
            .filter(LegacyId.last_updated_datetime >= before)
            .filter(LegacyId.last_updated_datetime <= after)
        ).count() == set_count


@pytest.mark.parametrize(
    "set_count",
    [
        (1),
        (10),
    ],
)
def test__ui_print_bioresource_pack(client, faker, set_count):
    user = login(client, faker)
    add_all_studies(user)

    before = datetime.datetime.utcnow()

    resp = client.get(url_for('ui.label_print', set='BioresourcePack', count=set_count, _external=True))

    after = datetime.datetime.utcnow()

    assert resp.status_code == 302
    assert resp.location == url_for('ui.labels', _external=True)

    provider = BioresourceIdProvider.query.filter_by(prefix='BR').first()

    assert (BioresourceId.query
            .filter_by(bioresource_id_provider_id=provider.id)
            .filter(BioresourceId.last_updated_datetime >= before)
            .filter(BioresourceId.last_updated_datetime <= after)
        ).count() == set_count


@pytest.mark.parametrize(
    "pack_name, aliquots_per_participant, set_count, site_name",
    [
        ("BriccsKetteringPack", 1, 1, 'KETTERING'),
        ("BriccsKetteringPack", 1, 10, 'KETTERING'),
    ],
)
def test__ui_print_pack_aliquots(client, faker, pack_name, set_count, aliquots_per_participant, site_name):
    user = login(client, faker)
    add_all_studies(user)

    ali_provider = SequentialIdProvider.query.filter_by(name=site_name + ' ' + ID_NAME_BRICCS_ALIQUOT).first()

    before_number = ali_provider.last_number

    before = datetime.datetime.utcnow()

    resp = client.get(url_for('ui.label_print', set=pack_name, count=set_count, _external=True))

    after = datetime.datetime.utcnow()

    assert resp.status_code == 302
    assert resp.location == url_for('ui.labels', _external=True)

    ali_provider = SequentialIdProvider.query.filter_by(name=site_name + ' ' + ID_NAME_BRICCS_ALIQUOT).first()

    assert ali_provider.last_number == before_number + (aliquots_per_participant * set_count)

    if aliquots_per_participant > 0:
        assert before < ali_provider.last_updated_datetime < after
        assert ali_provider.last_updated_by_user_id == user.id


@pytest.mark.parametrize(
    "pack_name, ids_per_prefix_per_sample, set_count",
    [
        (
            "BravePack",
            {
                "BavPt": 1,
                "BavSa": 5,
                "BavFm": 1,
            },
            1,
        ),
        (
            "BravePolandPack",
            {
                "BavPl": 1,
                "BavSa": 5,
                "BavFm": 1,
            },
            1,
        ),
        (
            "BraveExternalPack",
            {
                "BavXPt": 1,
                "BavSa": 3,
                "BavFm": 1,
            },
            1,
        ),
        (
            "CaePack",
            {
                "CaePt": 1,
                "CaeSa": 3,
            },
            1,
        ),
        (
            "CardiometPack",
            {
                "CarPt": 1,
                "CarSa": 17,
            },
            1,
        ),
        (
            "CiaPack",
            {
                "CiaPt": 1,
                "CiaSa": 2,
            },
            1,
        ),
        (
            "DiscordancePack",
            {
                "DisPt": 1,
            },
            1,
        ),
        (
            "FastPack",
            {
                "FST": 1,
            },
            1,
        ),
        (
            "IndapamidePack",
            {
                "IndPt": 1,
                "IndSa": 16,
            },
            1,
        ),
        (
            "LentenPack",
            {
                "LenPt": 1,
                "LenSa": 12,
            },
            1,
        ),
        (
            "LimbPack",
            {
                "LMbPt": 1,
                "LMbSa": 2,
            },
            1,
        ),
        (
            "PredictPack",
            {
                "PrePt": 1,
                "PreSa": 5,
            },
            1,
        ),
        (
            "PreeclampsiaPack",
            {
                "PePt": 1,
                "PeSa": 5,
            },
            1,
        ),
        (
            "ScadPack",
            {
                "ScPt": 1,
                "ScSa": 7,
            },
            1,
        ),
        (
            "ScadBloodOnlyPack",
            {
                "ScPt": 1,
                "ScSa": 3,
            },
            1,
        ),
        (
            "ScadFamilyPack",
            {
                "ScFm": 1,
            },
            1,
        ),
        (
            "SpiralPack",
            {
                "SpPt": 1,
            },
            1,
        ),
    ],
)
def test__ui_print_pseudorandom_packs(client, faker, pack_name, ids_per_prefix_per_sample, set_count):
    user = login(client, faker)
    add_all_studies(user)

    before = datetime.datetime.utcnow()

    resp = client.get(url_for('ui.label_print', set=pack_name, count=set_count, _external=True))

    after = datetime.datetime.utcnow()

    assert resp.status_code == 302
    assert resp.location == url_for('ui.labels', _external=True)

    for prefix, expected in ids_per_prefix_per_sample.items():
        provider = PseudoRandomIdProvider.query.filter_by(prefix=prefix).first()
        actual = (PseudoRandomId.query
            .filter_by(pseudo_random_id_provider=provider).count()
        )
        assert actual == expected
