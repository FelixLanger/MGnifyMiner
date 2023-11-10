from pathlib import Path
from typing import Union

import pandas as pd

from mgyminer.config import load_config
from mgyminer.wrappers.hmmer import esl_sfetch

config = load_config()


def export_sequences(args):
    """
    Export sequences from filters to FASTA format
    """
    fetcher = esl_sfetch()
    results = pd.read_csv(args.filter)
    target_ids = results.target_name.drop_duplicates().to_list()
    if args.seqdb:
        seqdb = args.seqdb
    else:
        seqdb = config["files"]["seqdb"]
    fetcher.run(seqdb, target_ids, args.output)


def mgyp_to_id(mgyp: str) -> int:
    """
    Strip MGYP beginning and leading zeroes from a MGYP accession

    :param mgyp: Standard MGnify MGYP protein accession
    :return: Plain protein ID without leading MGYP and zeroes
    """
    return int(mgyp.lstrip("MGYP0"))


def proteinID_to_mgyp(proteinid: Union[str, int]) -> str:
    """
    Convert a protein ID into MGnify protein accession

    :param proteinid: numeric protein ID
    :return: MGnify MGYP accession
    """
    if isinstance(proteinid, str):
        proteinid = int(proteinid)
    return "MGYP%012d" % int(proteinid)


def tryfloat(value: str) -> Union[str, float]:
    """
    Test if a string can be converted to a float and return that given float if possible
    This is useful for scientific notations that are parsed from the command line as strings
    such as 1E-15, 1e5, etc. so that they can be used as floats and used as such later on.
    :param value: string that should be checked if it can be represented as float
    :return: float of value if it can be represented as such, else return initial string
    """
    try:
        return float(value)
    except ValueError:
        return value


def write_list_to_file(lst: list, outfile: Union[str, Path]):
    """
    Write a list to a file with every item in list in a new line.
    :param lst: List to write to file
    :param outfile: Path to file
    :return: Path
    """
    with open(outfile, "wt") as name_file:
        for item in lst:
            name_file.write(f"{item} \n")
    return Path(outfile)
