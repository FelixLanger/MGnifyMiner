import hashlib

from mgyminer.wrappers.hmmer import PHmmer


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


def test_phmmer_run(tmpdir):
    phmmer = PHmmer(1)
    hmmer_output = tmpdir.join("hmmer.out")
    tbl = tmpdir.join("tbl.txt")
    domtbl = tmpdir.join("domtbl.txt")
    alignment = tmpdir.join("alignment.sto")
    phmmer.run(
        seqfile="data/sequence_files/query.fa",
        seqdb="data/sequence_files/seqdb.fa",
        output_file=hmmer_output,
        tblout=tbl,
        domtblout=domtbl,
        alignment=alignment,
    )
    assert get_file_hash(hmmer_output) == "9229149ca98b38f3bfb7d27df60829db"
    assert get_file_hash(tbl) == "3f1eecacfea8b9d02e88c9e1ac1006c1"
    assert get_file_hash(domtbl) == "ad8e29dc35bcf765f3040ce733cb8519"
    assert get_file_hash(alignment) == "72f04231ffc328ba5fed4e62b9170367"
