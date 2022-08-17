import tempfile
from typing import Union

import pandas as pd

from mgyminer.config import config
from mgyminer.phyltree import esl_sfetcher


def export_sequences(args):
    """
    Export sequences from filters to FASTA format
    """
    fetcher = esl_sfetcher()
    results = pd.read_csv(args.filter)
    if args.seqdb:
        seqdb = args.seqdb
    else:
        seqdb = config["seqdb"]
    with tempfile.NamedTemporaryFile() as temp:
        results["target_name"].drop_duplicates().to_csv(
            temp.name, index=False, header=False
        )
        fetcher.run(seqdb, temp.name, args.output, args=["-f"])


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
