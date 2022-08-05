import hashlib
import shutil
from pathlib import Path

from mgyminer.wrappers.hmmer import PHmmer, esl_sfetch


def get_file_hash(file):
    """
    Get the md5 hash of file without the # commented lines
    :param file: file to hash
    :return: md5 hash digest
    """
    md5 = hashlib.md5()
    with open(file, "rt") as fin:
        for line in fin.readlines():
            if not line.startswith("#"):
                md5.update(line.encode("utf-8"))
    return md5.hexdigest()


def test_phmmer_run(tmpdir, queryseq, seqdb):
    phmmer = PHmmer(1)
    hmmer_output = tmpdir.join("hmmer.out")
    tbl = tmpdir.join("tbl.txt")
    domtbl = tmpdir.join("domtbl.txt")
    alignment = tmpdir.join("alignment.sto")
    phmmer.run(
        seqfile=queryseq,
        seqdb=seqdb,
        output_file=hmmer_output,
        tblout=tbl,
        domtblout=domtbl,
        alignment=alignment,
    )
    assert get_file_hash(hmmer_output) == "9229149ca98b38f3bfb7d27df60829db"
    assert get_file_hash(tbl) == "3f1eecacfea8b9d02e88c9e1ac1006c1"
    assert get_file_hash(domtbl) == "ad8e29dc35bcf765f3040ce733cb8519"
    assert get_file_hash(alignment) == "72f04231ffc328ba5fed4e62b9170367"


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
