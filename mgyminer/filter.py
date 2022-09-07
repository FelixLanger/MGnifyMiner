import json
import re
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


def filter(args):

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
    # get input files
    results_file = args.input
    results_basedir = results_file.parents[0]
    if args.alignment:
        alignment = args.alignment
    elif (results_basedir / "alignment.json").exists():
        alignment = results_basedir / "alignment.json"
    else:
        sys.exit("Wrong or missing alignment file. Please use the --alignment flag")

    results_table = proteinTable(args.input)

    with open(alignment, "r") as fin:
        alignment_dict = json.load(fin)

    filters = args.residue
    for filter in filters:
        selection = overlapping_targets(filter, results_table.df)
        hits = check_residue(selection, alignment_dict, filter)
        filter_name = "_".join(filter)
        results_table.df[filter_name] = results_table.df["target_name"].map(hits)
        results_table.df.dropna(inplace=True)

    if args.output:
        results_table.save(args.output)
    else:
        print(results_table.df.to_string())


def overlapping_targets(args, results_table):
    """
    returns a list of target proteins whos alignment overlaps with the query residue
    :param args:
    :param results_table:
    :return:
    """
    residue_coordinate = int(args[0])
    selection = (
        results_table.loc[
            (results_table["hmm_from"] <= residue_coordinate)
            & (results_table["hmm_to"] >= residue_coordinate),
            ["target_name", "ali_from", "ali_to"],
        ]
        .to_string(header=False, index=False, index_names=False)
        .split("\n")
    )
    selection = [element.split() for element in selection]

    return selection


def check_residue(selection, alignment_dict, filter):
    residue_coordinate = int(filter[0])
    ex_inc = filter[1]
    residues = [residue.upper() for residue in filter[2:]]

    matches = {}

    for element in selection:
        entry = alignment_dict["-".join(element)]
        relative_coordinate = residue_coordinate - int(entry["query_start"])
        target_index = index_on_target(relative_coordinate, entry["query_seq"])
        residue = entry["target_seq"][target_index]
        if ex_inc == "include":
            if residue in residues:
                matches[element[0]] = residue
            else:
                continue
        if ex_inc == "exclude":
            if residue not in residues:
                matches[element[0]] = residue
    return matches


def index_on_target(pos, query_seq):
    inserts = query_seq[: pos + 1].count(".")
    residues = pos - inserts
    index = pos
    while residues != pos:
        index += 1
        inserts = query_seq[: index + 1].count(".")
        residues = index - inserts
    return index


# def parse_domtable(file):
#
#     column_names = [
#         "target_name",
#         "target_accession",
#         "tlen",
#         "query_name",
#         "query_accession",
#         "qlen",
#         "e-value",
#         "score",
#         "bias",
#         "ndom",
#         "ndom_of",
#         "c-value",
#         "i-value",
#         "dom_score",
#         "dom_bias",
#         "hmm_from",
#         "hmm_to",
#         "ali_from",
#         "ali_to",
#         "env_from",
#         "env_to",
#         "acc",
#         "description",
#     ]
#
#     convert_dict = {
#         "target_name": str,
#         "target_accession": str,
#         "tlen": int,
#         "query_name": str,
#         "query_accession": str,
#         "qlen": int,
#         "e-value": float,
#         "score": float,
#         "bias": float,
#         "ndom": int,
#         "ndom_of": int,
#         "c-value": float,
#         "i-value": float,
#         "dom_score": float,
#         "dom_bias": float,
#         "hmm_from": int,
#         "hmm_to": int,
#         "ali_from": int,
#         "ali_to": int,
#         "env_from": int,
#         "env_to": int,
#         "acc": float,
#         "description": str,
#     }
#
#     closeit = False
#     if isinstance(file, str):
#         file = Path(file)
#
#     if isinstance(file, Path):
#         file = open(file, "r")
#         closeit = True
#
#     rows = []
#     for line in csv.reader(decomment(file), delimiter=" ", skipinitialspace=True):
#         row = [item for item in line]
#         row[22] = " ".join(row[22:])
#         del row[23:]
#         rows.append(row)
#
#     if closeit:
#         file.close()
#
#     dom_table_df = pd.DataFrame(rows, columns=column_names)
#     dom_table_df = dom_table_df.astype(convert_dict)
#     return dom_table_df
#
#
# def decomment(rows):
#     for row in rows:
#         if row.startswith("#"):
#             continue
#         yield row

#
# def calculate_coverage(df):
#     df["coverage_hit"] = round((df["ali_to"] - df["ali_from"]) / df["tlen"], 2)
#     df["coverage_query"] = round((df["ali_to"] - df["ali_from"]) / df["qlen"], 2)


def _extract_range(threshold):
    # extend regex to allow floats in args directly to set threshold more precisely
    # [+-]?(\d+\.?\d*)|(\.\d+)
    regex = r"(\d+)"
    threshold_range = sorted([float(x) / 100 for x in re.findall(regex, threshold)])
    return threshold_range


# def alignments(file):
#     closeit = False
#     if isinstance(file, str):
#         file = Path(file)
#
#     if isinstance(file, Path):
#         file = open(file, "r")
#         closeit = True
#
#     alignment_upcomming = False
#     alignment = []
#     for line in decomment(file):
#         if alignment_upcomming is True:
#             alignment.append(line)
#             if len(alignment) > 2:
#                 alignment_upcomming = False
#                 yield alignment
#         elif line.startswith("  =="):
#             alignment_upcomming = True
#             alignment = []
#         else:
#             continue
#     if closeit:
#         file.close()


def end_of_column(string):
    found_letter = False
    for count, character in enumerate(string):
        if character == " ":
            if found_letter:
                return count
            else:
                continue
        else:
            found_letter = True


# def get_alignment_consensus(file):
#     alignments_dict = {}
#     for alignment in alignments(file):
#         # get the start index of the consensus sequence.
#         # problem: amount of leading witespaces is dependend on the length of query or target sequence but needs to
#         # be exactly calculated because whitespaces in the consensus stand for mismatches of the two aligned sequences
#         # Solution: count characters until you hit the first whitespace after hitting letters. Doing it once to get
#         # lenght until the name. doing it twice to get characters until the end of the start coordinates.
#         temp_index = end_of_column(alignment[2])
#         start_index = temp_index + end_of_column(alignment[2][temp_index:]) + 1
#         consensus = alignment[1][start_index:].strip("\n")
#         query_id, query_start, query_seq, query_end = alignment[0].split()
#         target_id, target_start, target_seq, target_end = alignment[2].split()
#         key = f"{target_id}-{target_start}-{target_end}"
#         perc_ident, perc_sim = calculate_identity_similarity(consensus)
#         alignments_dict[key] = {
#             "consensus": consensus,
#             "target_start": target_start,
#             "target_end": target_end,
#             "target_seq": target_seq,
#             "query_start": query_start,
#             "query_end": query_end,
#             "query_seq": query_seq,
#             "perc_ident": perc_ident,
#             "perc_sim": perc_sim,
#         }
#     return alignments_dict


def calculate_identity_similarity(consensus):
    identical = 0
    similar = 0
    for character in consensus:
        if character == " ":
            continue
        elif character == "+":
            similar += 1
        else:
            identical += 1

    percent_identity = round(identical / len(consensus) * 100, 2)
    percent_similarity = round((identical + similar) / len(consensus) * 100, 2)

    return percent_identity, percent_similarity


def add_sim_ident(df, alignment_dict):
    df["similarity"] = (
        df["target_name"]
        + "-"
        + df["ali_from"].astype(str)
        + "-"
        + df["ali_to"].astype(str)
    )
    df["identity"] = df["similarity"]
    df["similarity"] = df["similarity"].apply(lambda x: alignment_dict[x]["perc_sim"])
    df["identity"] = df["identity"].apply(lambda x: alignment_dict[x]["perc_ident"])


def plot_residue_histogram(args):
    results_file = args.input
    results_basepath = results_file.parents[0]
    alignments = results_basepath / "alignment.json"
    residue = int(args.residue)
    plotwidth = args.plotwidth

    with open(alignments, "r") as fin:
        alignment_dict = json.load(fin)

    # Get residue counts data
    found = []
    for key, alignment in alignment_dict.items():
        if (
            int(alignment["query_start"]) <= residue
            and int(alignment["query_end"]) >= residue
        ):
            relative_coordinate = residue - int(alignment["query_start"])
            target_index = index_on_target(relative_coordinate, alignment["query_seq"])
            found.append(alignment["target_seq"][target_index])
    found = Counter(found).most_common()

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


cfg = config
