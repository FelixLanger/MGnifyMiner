import re
from pathlib import Path
from typing import Tuple, Union

import numpy as np
import pandas as pd
from pandas import DataFrame


def extract_alignments(hmmer_out: Union[Path, str]) -> dict:
    """
    Takes hmmer standard output file (with notextwidth! option) and creates a dict with alignment
    and similarity and identity metrics
    :param hmmer_out: Path to hmmer output
    :return: alignment dictionary
    """
    alignments_dict = {}
    for alignment in alignments(hmmer_out):
        start, end = _start_end_coordinates(alignment[2])
        consensus = alignment[1][start:end]
        query_id, query_start, query_seq, query_end = alignment[0].split()
        target_id, target_start, target_seq, target_end = alignment[2].split()
        key = f"{target_id}-{target_start}-{target_end}"
        perc_ident, perc_sim = calculate_identity_similarity(consensus)
        alignments_dict[key] = {
            "consensus": consensus,
            "target_start": int(target_start),
            "target_end": int(target_end),
            "target_seq": target_seq,
            "query_start": int(query_start),
            "query_end": int(query_end),
            "query_seq": query_seq,
            "perc_ident": perc_ident,
            "perc_sim": perc_sim,
        }
    return alignments_dict


def calculate_identity_similarity(
    consensus: str, digit: int = 1
) -> Tuple[float, float]:
    """
    Calculate sequence similarity and identity values from a hmmer alignment consensus string
    :param consensus: hmmer consensus sequence
    :param digit: digits after point to keep
    :return: (identity_percentage, similarity_percentage)
    """
    length = len(consensus)
    similar = consensus.count("+")
    mismatch = consensus.count(" ")
    identical = length - mismatch - similar

    percent_identity = round(identical / length * 100, digit)
    percent_similarity = round((identical + similar) / length * 100, digit)

    return percent_identity, percent_similarity


def _start_end_coordinates(alignment: str) -> Tuple[int, int]:
    """
    Extract the start and end coordinates of the third hmmer alignment string.
    The alignment string needs to be the target section of the alignment with MGYP ID.
    It removes starting whitespaces, sequence name and start, end coords of the protein.
    :param alignment: alignment string
    :return: (start, end) coordinates of alignment string
    """
    start_pattern = re.compile(r"\s*MGYP\d*\s+\d+\s{1}")
    end_pattern = re.compile(r"\s\d+\s*$")
    alignment_start = start_pattern.match(alignment).end()
    alignment_end = end_pattern.search(alignment).start()
    return alignment_start, alignment_end


def alignments(file: Union[Path, str]):
    """
    Generator for going through the alignments in a HMMER output file with no textwidth
    formatting.
    :param file:
    :return:
    """
    closeit = False
    if isinstance(file, str):
        file = Path(file)

    if isinstance(file, Path):
        file = open(file, "r")
        closeit = True

    alignment_upcomming = False
    alignment = []
    for line in decomment(file):
        if alignment_upcomming is True:
            alignment.append(line.strip("\n"))
            if len(alignment) > 2:
                alignment_upcomming = False
                yield alignment
        elif line.startswith("  =="):
            alignment_upcomming = True
            alignment = []
        else:
            continue
    if closeit:
        file.close()


def decomment(rows):
    """
    Generator to return a file row by row without # comments
    :param rows:
    :return:
    """
    for row in rows:
        if row.startswith("#"):
            continue
        yield row


def parse_hmmer_domtable(domtable: Union[Path, str]) -> pd.DataFrame:
    """
    Parse HMMER domain Table to pandas DataFrame
    :param domtable: Path to domain table file
    :return: domain table pandas DataFrame
    """
    column_names = [
        "target_name",
        "target_accession",
        "tlen",
        "query_name",
        "query_accession",
        "qlen",
        "e-value",
        "score",
        "bias",
        "ndom",
        "ndom_of",
        "c-value",
        "i-value",
        "dom_score",
        "dom_bias",
        "hmm_from",
        "hmm_to",
        "ali_from",
        "ali_to",
        "env_from",
        "env_to",
        "acc",
    ]

    proteinTable = pd.read_csv(
        domtable,
        sep=r"\s+",
        comment="#",
        usecols=range(len(column_names)),
        names=column_names,
        dtype={
            "target_name": str,
            "target_accession": str,
            "tlen": int,
            "query_name": str,
            "query_accession": str,
            "qlen": int,
            "e-value": np.object_,
            "score": np.object_,
            "bias": np.object_,
            "ndom": int,
            "ndom_of": int,
            "c-value": np.object_,
            "i-value": np.object_,
            "dom_score": np.object_,
            "dom_bias": np.object_,
            "hmm_from": int,
            "hmm_to": int,
            "ali_from": int,
            "ali_to": int,
            "env_from": int,
            "env_to": int,
            "acc": np.object_,
        },
        engine="python",
    )

    # Calculate coverages
    proteinTable["coverage_hit"] = round(
        (proteinTable["ali_to"] - proteinTable["ali_from"])
        / proteinTable["tlen"]
        * 100,
        2,
    )

    proteinTable["coverage_query"] = round(
        (proteinTable["ali_to"] - proteinTable["ali_from"])
        / proteinTable["qlen"]
        * 100,
        2,
    )

    return proteinTable


def parse_hmmer_table(domtable: Union[Path, str]) -> DataFrame:
    """
    Parse HMMER Table to pandas DataFrame
    :param domtable: Path to domain table file
    :return: domain table pandas DataFrame
    """
    table = pd.read_csv(
        domtable,
        sep=r"\s+",
        comment="#",
        index_col=False,
        names=[
            "target_name",
            "target_accession",
            "query_name",
            "query_accession",
            "e-value",
            "score",
            "bias",
            "best1_e-value",
            "best1_score",
            "best1_bias",
            "exp",
            "reg",
            "clu",
            "ov",
            "env",
            "dom",
            "rep",
            "inc",
            "description of target",
        ],
    )
    return table
