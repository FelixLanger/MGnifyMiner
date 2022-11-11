import logging
import tempfile
from pathlib import Path
from typing import Optional, Union

import requests

from mgyminer.config import config
from mgyminer.parsers import parse_hmmer_table
from mgyminer.proteinTable import proteinTable
from mgyminer.utils import write_list_to_file
from mgyminer.wrappers.hmmer import EslAlimanip, Hmmbuild, Hmmsearch


class StructureDownloader:
    @staticmethod
    def download_file(url: str, outfile: Union[str, Path]) -> bool:
        response = requests.get(url)
        if response.ok:
            open(outfile, "wb").write(response.content)
            return True
        else:
            logging.warning("Encountered problems downloading file from %s", url)
            return False

    def download_alphafold(self, accession: str, outfile: Union[str, Path]) -> bool:
        """
        Download pdb file from AlphaFold to outfile for given accession
        :param accession: accession of AlphaFold entry
        :param outfile: file name to store .pdb file
        :return: bool True if successfully, false if failed to find file
        """
        url = "https://alphafold.ebi.ac.uk/files/"
        dl_link = url + accession + "-model_v3.pdb"
        return self.download_file(dl_link, outfile)

    def download_pdb(self, accession: str, outfile: Union[str, Path]) -> bool:
        """
        Download pdb file from PDB to outfile for given accession
        :param accession: accession of PDB entry
        :param outfile: file name to store .pdb file
        :return: bool True if successfully, false if failed to find file
        """
        url = "https://files.rcsb.org/download/"
        dl_link = url + accession + ".pdb"
        return self.download_file(dl_link, outfile)


def get_sto_entries(sto_alignment):
    """
    Get the names of all entries in a stockholm alignment.
    :param sto_alignment: Path to stockholm alignment
    :return: list of ids
    """
    with open(sto_alignment, "rt") as alignment:
        entries = [line.split()[1] for line in alignment if line.startswith("#=GS")]
    return entries


def remove_entries(selection, sto_entries):
    """
    Remove entries from stockholm alignment entry list
    :param selection: List of ids that should be removed from stockholm list
    :param sto_entries: Stockholm alignment entries
    :return:
    """
    id_dict = {}
    for entry in sto_entries:
        accession = entry.split("/")[0]
        if accession not in id_dict:
            id_dict[accession] = [entry]
        else:
            id_dict[accession].append(entry)
    ids_alignment = set(id_dict.keys()) - set(selection)
    ids_to_remove = []
    for entry in ids_alignment:
        ids_to_remove.extend(id_dict[entry])
    return ids_to_remove
    # Same thing in one line but much slower for huge lists
    # return [entry for entry in sto_entries if not any(map(entry.startswith, selection))]


def filter_msa(msa: Path, selection: set, outfile: Union[str, Path]):
    """
    Use esl-Alimanip to filter out entries from a Stockholm alignment and save
    the filtered alignment to a new file.
    :param msa: Path to the input Stockholm alignment
    :param selection: Set of MGYP accessions whose entries should be kept
    :param outfile: Path to output file
    :return: bool of filtering was sucessful
    """
    sto_entries = get_sto_entries(msa)
    entries_to_filter = remove_entries(selection, sto_entries)
    msa_filter = EslAlimanip()
    with tempfile.TemporaryDirectory() as temp_dir:
        id_file = Path(temp_dir) / "sto_entries.txt"
        write_list_to_file(entries_to_filter, id_file)
        return msa_filter.run(msa, outfile, id_file)


def searchDB(msa: Path, database: Path, outdir: Path, outfile: Optional[Path] = None):
    hmmsearch = Hmmsearch()
    hmmbuild = Hmmbuild()

    hmm = outdir / (msa.stem + ".hmm")
    hmmbuild.run(hmm, msa)
    if not outfile:
        outfile = msa.with_suffix(".txt")
        tblout = msa.with_suffix(".tbl")
    else:
        tblout = outfile.with_suffix(".tbl")
    return hmmsearch.run(
        hmm,
        database,
        outfile,
        tblout=tblout,
    )


def best_match(tbl: Path, coverage: bool = False, n: int = 1, cutoff: float = 1e-5):
    matches = parse_hmmer_table(tbl)
    considered_hits = matches[matches["e-value"] < cutoff]
    if coverage:
        best = considered_hits.nlargest(n, "coverage", keep="first")
    else:
        best = considered_hits.nsmallest(n, "e-value", keep="first")
    return best["target_name"]


def fetch_structure(
    msa: Union[str, Path],
    selectionTable: proteinTable,
    analysis_name: str,
    outdir: Optional[Union[str, Path]] = None,
    best_n: int = 1,
    databases: Optional[dict] = dict(),
    alphafold=False,
    keep=False,
    coverage=False,
):
    if isinstance(msa, str):
        msa = Path(msa)

    if not outdir:
        outdir = msa.parent

    if keep:
        intermediate_dir = outdir
    else:
        tempdir = tempfile.TemporaryDirectory()
        intermediate_dir = Path(tempdir.name)

    if "PDB" in databases:
        pdb = databases["PDB"]
    else:
        pdb = config["files"]["PDB"]
    if "AlphaFold" in databases:
        alphafolddb = databases["AlphaFold"]
    else:
        alphafolddb = config["files"]["AlphaFold"]

    sdownload = StructureDownloader()

    structures = []
    selected_proteins = set(selectionTable.df["target_name"])
    filtered_msa = intermediate_dir / (analysis_name + ".sto")
    filter_msa(msa, selected_proteins, filtered_msa)
    # Search against PDB
    pdb_results = intermediate_dir / (filtered_msa.stem + "vsPDB.out")
    pdb_results_tbl = pdb_results.with_suffix(".tbl")
    searchDB(filtered_msa, pdb, intermediate_dir, pdb_results)
    best_pdb_hit = best_match(pdb_results_tbl, n=best_n, coverage=coverage)
    if not best_pdb_hit.empty:
        for accession in best_pdb_hit:
            accession = accession.split("_")[0]
            outfile = outdir / (analysis_name + f"-pdb_{accession}.pdb")
            if sdownload.download_pdb(accession, outfile):
                structures.append(outfile)
    if alphafold:
        af_results = intermediate_dir / (filtered_msa.stem + "vsAlphaFold.out")
        af_results_tbl = pdb_results.with_suffix(".tbl")
        searchDB(filtered_msa, alphafolddb, intermediate_dir, af_results)
        best_pdb_hit = best_match(af_results_tbl, n=best_n, coverage=coverage)
        if not best_pdb_hit.empty:
            for accession in best_pdb_hit:
                accession = accession.split(":")[1]
                outfile = outdir / (analysis_name + f"-pdb_{accession}.pdb")
                if sdownload.download_alphafold(accession, outfile):
                    structures.append(outfile)
    return structures


def fetch_structure_cli(args):
    selectionTable = proteinTable(args.input)
    msa = args.msa
    analysis_name = args.input.stem
    best_n = args.ntop
    alphafold = (args.alphafold,)
    keep = (args.keep,)
    fetch_structure(
        selectionTable=selectionTable,
        msa=msa,
        analysis_name=analysis_name,
        best_n=best_n,
        alphafold=alphafold,
        keep=keep,
    )
