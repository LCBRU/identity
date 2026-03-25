# -*- coding: utf-8 -*-

from identity.model.id import BioresourceIdProvider

def test_validate(client):
    iut = BioresourceIdProvider(prefix='BR')

    assert iut.validate('BR1010266P')
    assert iut.validate('BR1032887C')
    assert iut.validate('BR1066050Z')

    assert not iut.validate('BR1066050A')
    assert not iut.validate('CD1066050Z')
    assert not iut.validate('BR066050S')
