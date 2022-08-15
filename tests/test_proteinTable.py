import filecmp

import pandas as pd
import pytest

from mgyminer.proteinTable import proteinTable


@pytest.fixture
def mockTable(phmmer_out):
    return proteinTable(phmmer_out)


def test_sort(mockTable, phmmer_out):
    df = pd.read_csv(phmmer_out)
    columns = ["e-value", "identity"]
    for column in columns:
        ascending = mockTable.sort(column, ascending=True)
        descending = mockTable.sort(column, ascending=False)
        assert list(ascending.df[column]) == sorted(df[column])
        assert list(descending.df[column]) == sorted(df[column], reverse=True)
    descending = mockTable.sort(columns)
    column = columns[0]
    assert descending.df[column].iloc[0] == df[column].max()
    with pytest.raises(ValueError):
        mockTable.sort("notacolumn")


def test_threshold(mockTable):
    lessthan = mockTable.threshold("tlen", less=202)
    assert len(lessthan.df) == 4
    greaterthan = mockTable.threshold("tlen", greater=290)
    assert len(greaterthan.df) == 5
    inrange = mockTable.threshold("e-value", 127, 320)
    assert len(inrange.df) == 7
    with pytest.raises(ValueError):
        mockTable.threshold("target_name", 100)
    with pytest.raises(ValueError):
        mockTable.threshold("notacolumn", 100)


def test_save(tmp_path, mockTable, phmmer_out):
    test_output = tmp_path / "test_save.txt"
    mockTable.save(test_output)
    assert filecmp.cmp(test_output, phmmer_out)


def test_match(mockTable):
    subset = mockTable.match("target_name", "MGYP000062928162")
    assert len(subset.df) == 2
    subset = mockTable.match("tlen", 292)
    assert len(subset.df) == 1
    subset = mockTable.match("coverage_query", 99.66)
    assert len(subset.df) == 2
    with pytest.raises(ValueError):
        mockTable.match("notacolumn", "something")
