import pytest
import glob
import os
import csv
from identity.model.id import PseudoRandomIdProvider

@pytest.mark.slow
def test_all_numbers_unique(client):
    iut = PseudoRandomIdProvider(prefix='Tst')
    created = set()

    for i in range(iut._PRIME):
        x = iut._permuteQPR(i)
        assert x not in created
        created.add(x)


@pytest.mark.slow
# @pytest.mark.skip(reason="Not working for some reason")
def test_compare_to_expected(client):
    test_data_dir = os.path.join(
        os.path.dirname(__file__),
        'test_data',
        '*.csv',
    )

    for path in glob.glob(test_data_dir):
        iut = PseudoRandomIdProvider(prefix=os.path.splitext(os.path.basename(path))[0])

        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                assert iut._get_id(int(row[0])) == row[1]


# @pytest.mark.skip(reason="Not working for some reason")
def test_validate(client):
    iut = PseudoRandomIdProvider(prefix='TstPt')

    assert iut.validate('TstPt76378647J')
    assert not iut.validate('TstSa76378647L')
    assert not iut.validate('TstPt76378647D')
