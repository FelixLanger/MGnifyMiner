import pandas as pd
import pytest

from mgyminer.proteinTable import proteinTable


@pytest.fixture
def mockTable(phmmer_out):
    return proteinTable(phmmer_out)


def test_sort(mockTable, phmmer_out):
    df = pd.read_csv(phmmer_out)
    # Test if normal sorting works
    columns = ["e-value", "similarity", "identity"]
    for column in columns:
        ascending = mockTable.sort(column, ascending=True)
        descending = mockTable.sort(column, ascending=False)
        assert ascending.df[column].iloc[0] == df[column].min()
        assert descending.df[column].iloc[0] == df[column].max()
    descending = mockTable.sort(columns)
    column = columns[0]
    assert descending.df[column].iloc[0] == df[column].max()


def test_filter():
    assert False


def test_biome():
    assert False


def test_save():
    assert False
