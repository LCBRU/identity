from identity.model.id import PseudoRandomIdProvider


def test_all_numbers_unique():
    iut = PseudoRandomIdProvider(prefix='Tst')
    created = set()

    for i in range(iut._PRIME):
        x = iut._permuteQPR(i)
        assert x not in created
        created.add(x)

    print(max(created))

test_all_numbers_unique()