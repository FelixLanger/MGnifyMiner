import shutil
from pathlib import Path

from mgyminer.wrappers.hmmer import PHmmer, esl_sfetch
from tests.helpers import get_file_hash


def test_phmmer_run(tmp_path, queryseq, seqdb):
    phmmer = PHmmer(1)
    hmmer_output = tmp_path / "hmmer.out"
    tbl = tmp_path / "tbl.txt"
    domtbl = tmp_path / "domTable.txt.txt"
    alignment = tmp_path / "alignment.sto"
    phmmer.run(
        seqfile=queryseq,
        seqdb=seqdb,
        output_file=hmmer_output,
        tblout=tbl,
        domtblout=domtbl,
        alignment=alignment,
    )
    assert get_file_hash(hmmer_output) == "beba727bb4d85ae16d817689ddaa1fbb"
    assert get_file_hash(tbl) == "9dbfa9582f885ad77e07bac8508de355"
    assert get_file_hash(domtbl) == "268891fe80d262e9ed39afbc297ba48a"
    assert get_file_hash(alignment) == "981d34efafc91fcb4994b1bb095604d2"


def test_esl_sfetch_index(tmp_path, seqdb):
    # Prepare files
    test_db = Path(shutil.copy(seqdb, tmp_path))

    sfetcher = esl_sfetch()
    sfetcher.index(test_db)
    index_file = test_db.with_suffix(test_db.suffix + ".ssi")
    assert index_file.is_file()
    assert index_file.stat().st_size > 0
    assert len(list(tmp_path.glob("*.ssi"))) == 1


def test_sequence_fetch(tmp_path, seqdb):
    # Setup Keyfile
    with open(seqdb, "rt") as sequence_file:
        ids = [
            line.split()[0].strip(">") for line in sequence_file if line.startswith(">")
        ]
    test_db = Path(shutil.copy(seqdb, tmp_path))
    sfetcher = esl_sfetch()
    out_file = tmp_path / "sfetch_out.fa"
    sfetcher.run(sequence_file=test_db, sequence_ids=ids, out_file=out_file)
    assert get_file_hash(out_file) == get_file_hash(test_db)
