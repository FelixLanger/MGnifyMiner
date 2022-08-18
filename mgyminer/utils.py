from typing import Union

import pandas as pd

from mgyminer.config import config
from mgyminer.wrappers.hmmer import esl_sfetch


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


def mgyp_to_id(mgyp: str) -> str:
    """
    Strip MGYP beginning and leading zeroes from a MGYP accession

    :param mgyp: Standard MGnify MGYP protein accession
    :return: Plain protein ID without leading MGYP and zeroes
    """
    return mgyp.lstrip("MGYP0")


def proteinID_to_mgyp(id: Union[str, int]) -> str:
    """
    Convert a protein ID into MGnify protein accession

    :param id: numeric protein ID
    :return: MGnify MGYP accession
    """
    if isinstance(id, str):
        id = int(id)
    return "MGYP%012d" % int(id)


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
