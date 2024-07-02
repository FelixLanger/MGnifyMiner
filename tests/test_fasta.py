import tempfile

from mgyminer.fasta import (
    export_sequences,
    export_sequences_cli,
    fetch_sequences_from_fasta,
    write_fasta,
)
from mgyminer.proteintable import ProteinTable


def test_fetch_sequences_from_fasta(seqdb):
    seq_ids = ["MGYP001082675080", "MGYP000420419373", "nonexistent_seq"]
    sequences = fetch_sequences_from_fasta(seqdb, seq_ids)

    assert len(sequences) == 2  # Assuming seq1 and seq2 exist in seqdb.fa
    assert "MGYP001082675080" in sequences
    assert "MGYP000420419373" in sequences
    assert "nonexistent_seq" not in sequences


def test_write_fasta():
    sequences = {"seq1": "ATGC", "seq2": "GCTA"}
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".fasta") as temp_file:
        write_fasta(sequences, temp_file.name)
        temp_file.seek(0)
        content = temp_file.read()

    assert content == ">seq1\nATGC\n>seq2\nGCTA\n"


def test_export_sequences(seqdb):
    seq_ids = ["MGYP001082675080", "MGYP000420419373"]
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".fasta") as temp_file:
        export_sequences(seqdb, seq_ids, temp_file.name)
        temp_file.seek(0)
        content = temp_file.read().strip()

    assert content.startswith(">MGYP001082675080\n")
    assert ">MGYP000420419373\n" in content


def test_export_sequences_cli(seqdb, phmmer_out):
    protein_table = ProteinTable(phmmer_out)

    class Args:
        pass

    args = Args()
    args.seqdb = seqdb
    args.filter = phmmer_out
    args.output = "output.fasta"

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".fasta") as temp_file:
        args.output = temp_file.name
        export_sequences_cli(args)
        temp_file.seek(0)
        content = temp_file.read().strip()

    for seq_id in protein_table.unique_hits:
        assert f">{seq_id}\n" in content
