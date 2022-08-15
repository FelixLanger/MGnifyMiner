from pathlib import Path

import pytest

data_dir = Path(__file__).parent / "data"


@pytest.fixture
def seqdb():
    return data_dir / "sequence_files/seqdb.fa"


@pytest.fixture
def queryseq():
    return data_dir / "sequence_files/query.fa"


@pytest.fixture
def phmmer_out():
    return data_dir / "phmmer_results.csv"
