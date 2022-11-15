import gzip
import sys
from datetime import date
from io import StringIO

import requests
from Bio import SeqIO

PDB_SEQUENCES = "https://ftp.wwpdb.org/pub/pdb/derived_data/pdb_seqres.txt.gz"
ALPHAFOLD_SEQUENCES = "https://storage.cloud.google.com/public-datasets-deepmind-alphafold/sequences.fasta"


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


def download_file(url, outfile):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(outfile, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return outfile


def setup_cli(args):
    sources = ["AlphaFold", "PDB", "MGnify"]
    download_day = date.today().isoformat()
    if args.source not in sources:
        sys.exit(f"Source not found. Choose one of: {sources}")

    args.outdir.mkdir(parents=True, exist_ok=True)
    if args.source == "PDB":
        download_pdb_sequences(args.outdir / f"{download_day}-pdb_sequences.fasta")
