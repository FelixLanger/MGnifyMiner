import json
import string
import sys
from collections import Counter
from typing import List, Union

import mysql.connector
import numpy as np
import pandas as pd

from mgyminer.config import config
from mgyminer.proteinTable import proteinTable
from mgyminer.utils import tryfloat


def feat_filter(args):

    if args.match and any([args.upper, args.lower]):
        exit(
            "Only use match or upper/lower. Not both. Use [MgnifyMiner filter --help] for more info"
        )

    pt = proteinTable(args.input)
    if args.match:
        # if column is non-numeric convert value to string
        if pt.df[args.feature].dtypes == "O":
            value = str(args.match)
        else:
            value = tryfloat(args.match)
        pt = pt.match(args.feature, value)

    if any([args.upper, args.lower]):
        if args.upper is None:
            upper = np.PINF
        else:
            upper = tryfloat(args.upper)
        if args.lower is None:
            lower = np.NINF
        else:
            lower = tryfloat(args.lower)
        pt = pt.threshold(args.feature, greater=lower, less=upper)

    if args.output:
        pt.save(args.output)
    else:
        print(pt.df.to_string())


def sort(args):
    pt = proteinTable(args.input)
    pt = pt.sort(args.feature, ascending=args.ascending)
    if args.output:
        pt.save(args.output)
    else:
        print(pt.df.to_string())


def residue_filter(args):
    # check if alignment file is present in input dir
    results_file = args.input
    results_basedir = results_file.parents[0]
    if args.alignment:
        alignment_file = args.alignment
    elif (results_basedir / "alignment.json").exists():
        alignment_file = results_basedir / "alignment.json"
    else:
        sys.exit("Wrong or missing alignment file. Please use the --alignment flag")

    # load input files
    results_table = proteinTable(args.input)

    with open(alignment_file, "r") as fin:
        algnmt = alignment(json.load(fin))

    filters = args.residue
    for rfilter in filters:
        coordinate = rfilter[0]
        in_ex = rfilter[1]
        aa = rfilter[2:]
        coordinate = int(coordinate)
        # get all entries where aa in sequence matches reference
        matches = algnmt.match_residue(coordinate, aa)
        if in_ex == "exclude":
            # if aa should be excluded, get all sequences with overlap at specified coordinate
            # and substract all sequences that have the specified aas
            overlaps = [key for key, value in algnmt.overlaps_at(coordinate)]
            match_keys = set(overlaps) - set(matches.keys())
            # create new matches dict with only the sequences matching the criteria
            matches = alignment({match_id: algnmt[match_id] for match_id in match_keys})
        match_ids = matches.ids()
        results_table = proteinTable(
            results_table.df[results_table.df["target_name"].isin(match_ids)]
        )
        id_aa_mapping = {
            key.split("-")[0]: matches.corresponding_aa(key, coordinate)
            for (key, value) in matches.items()
        }
        filter_name = "_".join(rfilter)
        results_table.df[filter_name] = results_table.df["target_name"].map(
            id_aa_mapping
        )

    if args.output:
        results_table.save(args.output)
    else:
        print(results_table.df.to_string())


def plot_residue_histogram(args):
    results_file = args.input
    results_basepath = results_file.parents[0]
    alignments = results_basepath / "alignment.json"
    residue = int(args.residue)
    plotwidth = args.plotwidth

    with open(alignments, "r") as fin:
        alignment_dict = alignment(json.load(fin))

    found = alignment_dict.residue_distribution(residue).most_common()

    # Plot output
    max_value = max(count for label, count in found)
    increment = max_value / (plotwidth - 10)

    longest_label_length = max(len(label) for label, count in found)

    print(
        f"Hit residues corresponding to position {residue} on query sequence".center(
            plotwidth
        )
    )
    print(plotwidth * "=")
    for label, count in found:
        bar_chunks, remainder = divmod(int(count * 8 / increment), 8)
        bar = "█" * bar_chunks
        if remainder > 0:
            bar += chr(ord("█") + (8 - remainder))
        bar = bar or "▏"
        print(f"{label.rjust(longest_label_length)} ▏ {count:#4d} {bar}")


def domain_filter(args):
    hits = pd.read_csv(
        args.input, dtype={"biome": str, "PL": str, "UP": str, "CR": str}
    )
    if args.strict:
        matches = strict_select(args.arch)
    else:
        matches = loose_select(args.arch)
    results = pd.merge(matches, hits, left_on="MGYP", right_on="target_name")
    results = results[
        [column for column in results if column not in ["Pfams", "domain_names"]]
        + ["Pfams", "domain_names"]
    ]
    del results["MGYP"]
    if args.output:
        results.to_csv(args.output, index=False, sep=",")
    else:
        print(results.to_string())


def strict_select(pfams):
    proteindb = mysql.connector.connect(**cfg["mysql_test"])
    cursor = proteindb.cursor()
    conditions = f"pfams LIKE '%{pfams[0]}%'"
    for pfam in pfams[1:]:
        conditions += f" AND pfams LIKE '%{pfam}%'"
    statement = (
        f"SELECT pa.id, ar.pfams, ar.names FROM architecture ar LEFT JOIN protein_arch pa ON"
        f" ar.id = pa.arch_id WHERE {conditions}"
    )
    cursor.execute(statement)
    hits = pd.DataFrame(cursor.fetchall(), columns=["MGYP", "Pfams", "domain_names"])
    hits = hits.dropna()
    hits["MGYP"] = hits["MGYP"].astype(np.int64)
    if hits.empty:
        return hits
    hits["MGYP"] = hits["MGYP"].astype(int).apply(lambda x: f"MGYP{x:012d}")
    cursor.close()
    return hits


def loose_select(pfams):
    proteindb = mysql.connector.connect(**cfg["mysql_test"])
    cursor = proteindb.cursor()
    regex = "|".join(pfams)
    statement = (
        f"SELECT pa.id, ar.pfams, ar.names FROM architecture ar LEFT JOIN protein_arch pa ON"
        f" ar.id = pa.arch_id WHERE pfams REGEXP '{regex}'"
    )
    cursor.execute(statement)
    hits = pd.DataFrame(cursor.fetchall(), columns=["MGYP", "Pfams", "domain_names"])
    hits = hits.dropna()
    hits["MGYP"] = hits["MGYP"].astype(np.int64)
    cursor.close()
    if hits.empty:
        return hits
    else:
        hits["MGYP"] = hits["MGYP"].astype(int).apply(lambda x: f"MGYP{x:012d}")
        return hits


class alignment(dict):
    _TARSEQ_INSERT_TABLE = str.maketrans("", "", string.ascii_lowercase)

    def overlaps_at(self, coordinate):
        """
        Return all alignment entries where target sequences overlap
        with the query sequence at specified query residue.
        :param coordinate: Query sequence coordinate which should be aligned by target sequence
        :return: dict of overlap alignment entries
        """
        for key, value in self.items():
            if value["query_start"] <= coordinate <= value["query_end"]:
                yield key, value

    def match_residue(self, coordinate: int, aminoacid: Union[str, List[str]]):
        """
        Return all alignment entries that have a specific aminoacid at
        coordinate corresponding to query sequence
        :param coordinate: Coordinate corresponding to query sequence
        :param aminoacid: single or list of amino acids that should be present
        :return:
        """
        if isinstance(aminoacid, str):
            aminoacid = [aminoacid]

        aminoacid = [a.upper() for a in aminoacid]
        matches = []
        for key, value in self.overlaps_at(coordinate):
            target_without_inserts = value["target_seq"].translate(
                self._TARSEQ_INSERT_TABLE
            )
            relative_coordinate = coordinate - value["query_start"]
            if target_without_inserts[relative_coordinate] in aminoacid:
                matches.append(key)
        return alignment((entry, self[entry]) for entry in matches)

    def match_query(self, coordinate):
        """
        Return all entries of alignment where the entry matches the aminoacid of the query
        at the specified coordinate
        :param coordinate: Coordinate of the position in the query sequence
        :return:
        """
        matches = []
        for key, value in self.overlaps_at(coordinate):
            relative_coordinate = coordinate - value["query_start"]
            target_without_inserts = value["target_seq"].translate(
                self._TARSEQ_INSERT_TABLE
            )
            query_without_inserts = value["query_seq"].replace(".", "")
            if (
                target_without_inserts[relative_coordinate].lower()
                == query_without_inserts[relative_coordinate]
            ):
                matches.append(key)
        return alignment((entry, self[entry]) for entry in matches)

    def residue_distribution(self, coordinate):
        """
        Calculate the aminoacid distribution of all aligned sequences at a coordinate
        corresponding to the query sequence
        :param coordinate: Coordinate of the position in the query sequence
        :return: Counter of all aminoacids aligned to that coordinate
        """
        residues = []
        for key, value in self.overlaps_at(coordinate):
            relative_coordinate = coordinate - value["query_start"]
            target_without_inserts = value["target_seq"].translate(
                self._TARSEQ_INSERT_TABLE
            )
            residues.append(target_without_inserts[relative_coordinate])
        return Counter(residues)

    def ids(self):
        return {k.split("-")[0] for k in self.keys()}

    def corresponding_aa(self, key, coordinate):
        """
        Function to return the corresponding aminoacid on the aligned sequence at
        the coordinate corresponding to the reference.
        :param key:
        :param coordinate:
        :return:
        """
        value = self[key]
        relative_coordinate = coordinate - value["query_start"]
        target_without_inserts = value["target_seq"].translate(
            self._TARSEQ_INSERT_TABLE
        )
        return target_without_inserts[relative_coordinate]


cfg = config
