import shutil
from hashlib import md5
from pathlib import Path

from mgyminer.wrappers.hmmer import EslAlimanip, Hmmbuild, Hmmsearch, PHmmer, esl_sfetch
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
    with open(seqdb) as sequence_file:
        ids = [line.split()[0].strip(">") for line in sequence_file if line.startswith(">")]
    test_db = Path(shutil.copy(seqdb, tmp_path))
    sfetcher = esl_sfetch()
    out_file = tmp_path / "sfetch_out.fa"
    sfetcher.run(sequence_file=test_db, sequence_ids=ids, out_file=out_file)
    assert get_file_hash(out_file) == get_file_hash(test_db)


def test_hmmbuild_run(sto_ali, tmp_path):
    hmmbuilder = Hmmbuild()
    hmm_out = tmp_path / "test.hmm"
    hmmbuilder.run(hmmfile=hmm_out, msafile=sto_ali, single_seq=False)
    checksum = md5()
    with open(hmm_out) as fin:
        for line in fin.readlines()[11:]:
            if not line.startswith("#"):
                checksum.update(line.encode("utf-8"))
    assert checksum.hexdigest() == "3e5547af52d2b234342c35f83a2d89cb"


def test_hmmsearch_run(test_hmm, seqdb, tmp_path):
    hmmsearch = Hmmsearch()
    outfile = tmp_path / "hmmsearch.out"
    tlb_out = tmp_path / "hmmsearch.tbl"
    domtlb_out = tmp_path / "hmmsearch.domtbl"
    alignment = tmp_path / "hmmsearch.sto"
    hmmsearch.run(
        test_hmm,
        seqdb,
        outfile,
        tblout=tlb_out,
        domtblout=domtlb_out,
        alignment=alignment,
        notextw=True,
    )
    assert get_file_hash(outfile) == "2bb0a394ea2b14c964d75557ba07c195"
    assert get_file_hash(tlb_out) == "a1ca391ad3a67fc640292bdd1d65c2d3"
    assert get_file_hash(domtlb_out) == "e7a46fb0d0f560d329d8a08414ccdab0"
    assert get_file_hash(alignment) == "d09999713b23e74b72aec417cbfe6b97"


def test_alimanip_run(sto_ali, tmp_path):
    manip = EslAlimanip()
    filtered_ali = tmp_path / "filtered.sto"
    with open(tmp_path / "idfile", "w") as fout:
        fout.write("MGYP001082675080/61-129 \n")
        fout.write("MGYP001583336646/30-318")
    manip.run(msafile=sto_ali, output_file=filtered_ali, exclude_ids="infile")
    get_file_hash(filtered_ali, ignore_comments=False) == "b7f2e241fe55c2d9012e6f1763196329"
