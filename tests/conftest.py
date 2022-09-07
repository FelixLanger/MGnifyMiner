import json
from pathlib import Path

import pytest

from mgyminer.filter import alignment

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


@pytest.fixture
def alignmt():
    with open(data_dir / "alignment.json", "rt") as ali:
        return alignment(json.load(ali))
