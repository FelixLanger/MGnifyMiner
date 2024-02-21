import filecmp

import pandas as pd
import pytest

from mgyminer.proteinTable import proteinTable


@pytest.fixture
def mocktable(phmmer_out):
    return proteinTable(phmmer_out)


def test_sort(mocktable, phmmer_out):
    df = pd.read_csv(phmmer_out)
    columns = ["e-value", "identity"]
    for column in columns:
        ascending = mocktable.sort(column, ascending=True)
        descending = mocktable.sort(column, ascending=False)
        assert list(ascending.df[column]) == sorted(df[column])
        assert list(descending.df[column]) == sorted(df[column], reverse=True)
    descending = mocktable.sort(columns)
    column = columns[0]
    assert descending.df[column].iloc[0] == df[column].max()
    with pytest.raises(ValueError):
        mocktable.sort("notacolumn")


def test_threshold(mocktable):
    lessthan = mocktable.threshold("tlen", less=202)
    assert len(lessthan.df) == 6
    assert list(lessthan.df.target_name) == [
        "MGYP000754038055",
        "MGYP000604501205",
        "MGYP001394579466",
        "MGYP000062928162",
        "MGYP000062928162",
        "MGYP001450139400",
    ]
    greaterthan = mocktable.threshold("similarity", greater=55.5)
    assert len(greaterthan.df) == 8
    inrange = mocktable.threshold("e-value", 1e-77, 1e-10)
    assert list(inrange.df.target_name) == [
        "MGYP001583336646",
        "MGYP001082675080",
        "MGYP001082675080",
        "MGYP000754038055",
    ]
    with pytest.raises(ValueError):
        mocktable.threshold("target_name", 100)
    with pytest.raises(ValueError):
        mocktable.threshold("notacolumn", 100)


def test_save(tmp_path, mocktable, phmmer_out):
    test_output = tmp_path / "test_save.txt"
    mocktable.save(test_output)
    assert filecmp.cmp(test_output, phmmer_out)


def test_match(mocktable):
    subset = mocktable.match("query_name", "sp|P0A7B3|NADK_ECOLI")
    assert len(subset.df) == 13
    subset = mocktable.match("tlen", 292)
    assert len(subset.df) == 1
    subset = mocktable.match("coverage_query", 99.66)
    assert len(subset.df) == 2
    with pytest.raises(ValueError):
        mocktable.match("notacolumn", "something")
