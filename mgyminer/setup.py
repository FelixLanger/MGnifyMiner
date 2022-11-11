import gzip
from io import StringIO

import requests
from Bio import SeqIO

PDB_SEQUENCES = "https://ftp.wwpdb.org/pub/pdb/derived_data/pdb_seqres.txt.gz"


def download_pdb_sequences(outfile):
    """
    Download fasta for all protein sequences in PDB
    """
    r = requests.get(PDB_SEQUENCES, stream=True)
    text = gzip.decompress(r.content).decode("utf-8")
    fasta_io = StringIO(text)
    proteins = [
        rec
        for rec in SeqIO.parse(fasta_io, "fasta")
        if "mol:protein" in rec.description
    ]

    with open(outfile, "w") as fout:
        SeqIO.write(proteins, fout, "fasta")
