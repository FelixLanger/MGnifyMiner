import pyfastx

from mgyminer.proteintable import ProteinTable


def fetch_sequences(fasta_file, seq_ids):
    """
    Fetch sequences from a FASTA file given a list of sequence IDs.

    Parameters:
    - fasta_file: Path to the FASTA file.
    - seq_ids: A list of sequence IDs to fetch.

    Returns:
    A dictionary where keys are sequence IDs and values are sequences.
    """
    fasta = pyfastx.Fasta(fasta_file, build_index=True)
    sequences = {}

    for seq_id in seq_ids:
        try:
            sequence = fasta[seq_id]
            sequences[seq_id] = str(sequence.seq)
        except KeyError:
            print(f"Sequence ID {seq_id} not found in FASTA file.")

    return sequences


def sequences_to_fasta(sequences, output_file):
    """
    Export sequences to a new FASTA file.

    Parameters:
    - sequences: A dictionary of sequences to export, where keys are sequence IDs and values are sequences.
    - output_file: Path to the output FASTA file.
    """
    with open(output_file, "w") as f:
        for seq_id, sequence in sequences.items():
            f.write(f">{seq_id}\n{sequence}\n")


def fetch_sequences_cli(args):
    protein_table = ProteinTable(args.filter)
    seq_ids = protein_table.unique_hits
    if args.seqdb:
        sequences = fetch_sequences(args.seqdb, seq_ids)
    else:
        raise ValueError("Sequence database (--seqdb) is required for exporting sequences.")
    sequences_to_fasta(sequences, args.output)
