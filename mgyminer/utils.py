import hashlib
from json import JSONEncoder
from pathlib import Path
from typing import Union

import numpy as np
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


def contigID_to_mgyc(conticid: Union[str, int]) -> str:
    """
    Convert a protein ID into MGnify protein accession

    :param contigid: numeric protein ID
    :return: MGnify MGYP accession
    """
    if isinstance(conticid, str):
        conticid = int(conticid)
    return "MGYC%012d" % int(conticid)


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
    with open(outfile, "w") as name_file:
        for item in lst:
            name_file.write(f"{item} \n")
    return Path(outfile)


def create_md5_hash(input_string):
    """
    Generate an MD5 hash for a given input string.

    This function takes a string, encodes it into bytes, and then computes its MD5 hash.
    The resulting hash is returned in hexadecimal format. Note that MD5 is not secure against
    collision attacks and should not be used for cryptographic purposes.

    Args:
    input_string (str): The string to be hashed.

    Returns:
    str: The hexadecimal MD5 hash of the input string.
    """

    # Create an MD5 hash object
    hash_object = hashlib.md5()

    # Update the hash object with the bytes of the input string
    hash_object.update(input_string.encode())

    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()

    return hash_hex


def flatten_list(nested_list):
    flat_list = []
    for element in nested_list:
        if isinstance(element, list):
            flat_list.extend(flatten_list(element))
        else:
            flat_list.append(element)
    return flat_list


def dataframe_to_fasta(df, fasta_file):
    """
    Convert a DataFrame with protein IDs and sequences to a FASTA file.

    :param df: DataFrame with protein data. First column should be the ID, second column the sequence.
    :param fasta_file: Path to the output FASTA file.
    """
    with open(fasta_file, "w") as file:
        for index, row in df.iterrows():
            file.write(f">{row[0]}\n{row[1]}\n")


class NumpyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super().default(obj)


def biome_str_to_ids(biome_strs: list[str], biome_mapping: dict):
    """
    Converts a list of biome strings to a non-redundant list of corresponding biome IDs, including all specified biomes
    and their descendants in the biome hierarchy.

    Args:
        biome_strs (list[str]): A list of biome strings to be matched. These strings should correspond to the beginning
                                of the biome names in the biome_mapping dictionary to include all relevant descendants.
        biome_mapping (dict[int, str]): A dictionary mapping biome IDs (int) to their full hierarchical names (str).

    Returns:
        list[int]: A list of unique biome IDs that match the given biome strings and their descendants within the
                   hierarchy defined by biome_mapping.

    Example:
        >>> biome_mapping = {1: "root:Host-associated", 2: "root:Host-associated:Mammals"}
        >>> biome_strs = ["root:Host-associated"]
        >>> print(biome_str_to_ids(biome_strs, biome_mapping))
        [1, 2]
    """
    matching_biome_ids = set()
    for biome_str in biome_strs:
        for biome_id, biome_name in biome_mapping.items():
            if biome_name.startswith(biome_str):
                matching_biome_ids.add(biome_id)
    return list(matching_biome_ids)
