import tempfile
from typing import Union

import pandas as pd

from mgyminer.phyltree import esl_sfetcher


def export_sequences(args):
    """
    Export sequences from filters to FASTA format
    :param results:
    :return:
    """
    fetcher = esl_sfetcher()
    results = pd.read_csv(args.filter)
    with tempfile.NamedTemporaryFile() as temp:
        results["target_name"].drop_duplicates().to_csv(
            temp.name, index=False, header=False
        )
        fetcher.run("testSeqDB.fa", temp.name, args.output, args=["-f"])


def mgyp_to_id(mgyp: Union[str, int]) -> str:
    """
    Strip MGYP beginning and leading zeroes from a MGYP accession

    :param mgyps: Standard MGnify MGYP protein accession
    :return: Plain protein ID without leading MGYP and zeroes
    """
    return mgyp.lstrip("MGYP0")


def proteinID_to_mgyp(id: str) -> str:
    """
    Convert a protein ID into MGnigy protein accession

    :param id: numeric protein ID
    :return: MGnify MGYP accession
    """
    if isinstance(id, str):
        id = int(id)
    return "MGYP%012d" % int(id)
