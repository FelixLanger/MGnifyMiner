import logging
import tempfile
from pathlib import Path
from typing import Union

import requests
import yaml

from mgyminer.parsers import parse_hmmer_table
from mgyminer.wrappers.hmmer import Hmmbuild, Hmmsearch

config_root = Path(__file__).parents[1]
with open(config_root / "config.yaml") as configfile:
    cfg = yaml.load(configfile, Loader=yaml.CLoader)
pdb_location = cfg["pdb"]["location"]


class PDBDatabase:
    @staticmethod
    def fetch_pdb(accession: str, outfile: Union[str, Path]) -> bool:
        """
        Download pdb file from PDB to outfile for given accession
        :param accession: accession of PDB entry
        :param outfile: file name to store .pdb file
        :return: bool True if successfull, false if failed to find file
        """
        url = "https://files.rcsb.org/download/"
        dl_link = url + accession + ".pdb"
        response = requests.get(dl_link)
        if response.ok:
            open(outfile, "wb").write(response.content)
            return True
        else:
            logging.warning(
                "Problems fetching PDB structure with accession %s", accession
            )
            return False


class Structure_Fetcher:
    def __init__(self, ProteinTable):
        self.ProteinTable = ProteinTable
        self.hmmsearch = Hmmsearch()
        self.hmmbuild = Hmmbuild()
        self.hmm = None

    def fetch_pdb_structures(
        self, msa: Union[str, Path], ntop: int = 5, keep: bool = False
    ):
        """
        Fetch the ntop best structure hits similar to the results of the sequence search result
        :param ntop: number of structures to download
        :param keep: keep intermediate files if true
        :return:
        """
        # TODO: filter msa to only have protein table entries

        if isinstance(msa, str):
            msa = Path(msa)

        results_out = msa.parent
        if keep:
            out_dir = msa.parent
        else:
            temp_dir = tempfile.TemporaryDirectory()
            out_dir = Path(temp_dir.name)
        self.hmm = out_dir / (msa.stem + ".hmm")
        self.hmmbuild.run(self.hmm, msa)

        outfiles_stem = out_dir / (self.hmm.stem + "_vs_pdb")
        hmmsearch_tbl = outfiles_stem.with_suffix(".tbl")
        self.hmmsearch.run(
            self.hmm,
            pdb_location,
            outfiles_stem.with_suffix(".out"),
            tblout=hmmsearch_tbl,
        )
        results = parse_hmmer_table(hmmsearch_tbl)
        best = results.nsmallest(ntop, "e-value")
        best_accessions = best["target_name"].apply(lambda x: x.split("_")[0])
        for i, accession in enumerate(best_accessions):
            PDBDatabase.fetch_pdb(accession, results_out / f"{i}_{accession}.pdb")

        return True


def fetch_structure(args):
    sfetcher = Structure_Fetcher(args.input)
    sfetcher.fetch_pdb_structures(args.msa, ntop=args.ntop, keep=args.keep)
    return True
