import sys
import tempfile
from pathlib import Path
from typing import Union

import pandas as pd
import yaml

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


def find_config_file() -> Path:
    """
    Search through directories for mgyminer config file.
    Files are used by descending priority:
        - mgyminer.yaml in current working directory
        - .mgyminer.yaml in $HOME directory (dotfile)
    :return: Path to config_file
    """
    paths = list(
        filter(
            lambda x: x.exists(),
            [Path() / "mgyminer.yaml", Path.home() / ".mgyminer.yaml"],
        )
    )

    if paths:
        return paths[0]
    else:
        sys.exit("Exited\nCoun't find mgyminer.yaml config file")


def parse_config(config_file: Path) -> dict:
    """
    Parse the yaml config_file into Python dirctionary
    """
    with open(config_file) as configfile:
        cfg = yaml.load(configfile, Loader=yaml.CLoader)
    return cfg


def config():
    return parse_config(find_config_file())
