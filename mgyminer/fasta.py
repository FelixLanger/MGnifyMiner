import pyfastx

from mgyminer.proteintable import ProteinTable


def fetch_sequences_from_fasta(fasta_file, seq_ids):
    """
    Fetch sequences from a FASTA file given a list of sequence IDs.

    Parameters:
    - fasta_file: Path to the FASTA file.
    - seq_ids: A list of sequence IDs to fetch.

    Returns:
    A dictionary where keys are sequence IDs and values are sequences.
    """
    fasta = pyfastx.Fasta(str(fasta_file), build_index=True)
    sequences = {}

    for seq_id in seq_ids:
        try:
            sequence = fasta[seq_id]
            sequences[seq_id] = str(sequence.seq)
        except KeyError:
            print(f"Sequence ID {seq_id} not found in FASTA file.")

    return sequences


def write_fasta(sequences, output_file):
    """
    Write sequences to a FASTA file.

    Parameters:
    - sequences: A dictionary of sequences to write, where keys are sequence IDs and values are sequences.
    - output_file: Path to the output FASTA file.
    """
    with open(output_file, "w") as f:
        for seq_id, sequence in sequences.items():
            f.write(f">{seq_id}\n{sequence}\n")


def export_sequences(seqdb, seq_ids, output):
    """
    Fetch sequences from a FASTA file and export them to a new FASTA file.

    Parameters:
    - seqdb: Path to the input FASTA file.
    - seq_ids: A list of sequence IDs to fetch.
    - output: Path to the output FASTA file.
    """
    sequences = fetch_sequences_from_fasta(str(seqdb), seq_ids)
    write_fasta(sequences, output)


def export_sequences_cli(args):
    """
    CLI function to export sequences based on a protein table filter.

    Parameters:
    - args: Command-line arguments containing filter, seqdb, and output information.
    """
    if not args.seqdb:
        raise ValueError("Sequence database (--seqdb) is required for exporting sequences.")

    protein_table = ProteinTable(args.filter)
    seq_ids = protein_table.unique_hits
    export_sequences(args.seqdb, seq_ids, args.output)
