import csv
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd


def filter(args):
    # manage arguments
    hmmer_output_file = args.input
    results_basepath = hmmer_output_file.parents[0]
    dom_tbl_file = results_basepath / "dom_tbl.txt"
    # tbl_file = results_basepath / "tbl.txt"
    alignments = results_basepath / "alignments.json"

    # get table
    dom_tbl = parse_domtable(dom_tbl_file)
    calculate_coverage(dom_tbl)
    if alignments.is_file():
        with open(alignments, "r") as fin:
            aligmnent_dict = json.load(fin)

    else:
        aligmnent_dict = get_alignment_consensus(hmmer_output_file)
        with open(alignments, "w") as fout:
            json.dump(aligmnent_dict, fout)
    add_sim_ident(dom_tbl, aligmnent_dict)

    if args.eval:
        dom_tbl = dom_tbl[dom_tbl["e-value"] <= args.eval]

    if args.coverage:
        coverage_range = _extract_range(args.coverage)
        dom_tbl = dom_tbl[
            dom_tbl["coverage_query"].between(coverage_range[0], coverage_range[1])
        ]

    if args.sort:
        map = {
            "eval": "score",
            "coverage": "coverage_query",
            "similarity": "similarity",
            "identity": "identity",
        }
        if all(filters in map.keys() for filters in args.sort):
            columns = [map[v] for v in args.sort]
            columns.extend(
                ["target_name", "ndom"]
            )  # additionally sort by name and ndom to keep entries from one
            orientation = [
                False for column in columns
            ]  # protein together, ndom sort needs to be ascending to keep
            orientation[-1] = True  # domain order
            dom_tbl = dom_tbl.sort_values(by=columns, ascending=orientation)

    if args.output:
        dom_tbl.to_csv(args.output, index=False, sep=",")
    else:
        print(dom_tbl.to_string())


def residue_filter(args):
    # get input files
    results_file = args.input
    results_basepath = results_file.parents[0]
    alignments = results_basepath / "alignments.json"

    # read input files
    results_table = pd.read_csv(results_file)
    results_table["hmm_from"].astype(int)
    results_table["hmm_to"].astype(int)
    with open(alignments, "r") as fin:
        alignment_dict = json.load(fin)

    filters = args.residue
    for filter in filters:
        selection = overlapping_targets(filter, results_table)
        hits = check_residue(selection, alignment_dict, filter)
        filter_name = "_".join(filter)
        results_table[filter_name] = results_table["target_name"].map(hits)
        results_table.dropna(inplace=True)

    print(results_table.to_string())


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


def parse_domtable(file):

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
        "description",
    ]

    convert_dict = {
        "target_name": str,
        "target_accession": str,
        "tlen": int,
        "query_name": str,
        "query_accession": str,
        "qlen": int,
        "e-value": float,
        "score": float,
        "bias": float,
        "ndom": int,
        "ndom_of": int,
        "c-value": float,
        "i-value": float,
        "dom_score": float,
        "dom_bias": float,
        "hmm_from": int,
        "hmm_to": int,
        "ali_from": int,
        "ali_to": int,
        "env_from": int,
        "env_to": int,
        "acc": float,
        "description": str,
    }

    closeit = False
    if isinstance(file, str):
        file = Path(file)

    if isinstance(file, Path):
        file = open(file, "r")
        closeit = True

    rows = []
    for line in csv.reader(decomment(file), delimiter=" ", skipinitialspace=True):
        row = [item for item in line]
        row[22] = " ".join(row[22:])
        del row[23:]
        rows.append(row)

    if closeit:
        file.close()

    dom_table_df = pd.DataFrame(rows, columns=column_names)
    dom_table_df = dom_table_df.astype(convert_dict)
    return dom_table_df


def decomment(rows):
    for row in rows:
        if row.startswith("#"):
            continue
        yield row


def calculate_coverage(df):
    df["coverage_hit"] = round((df["ali_to"] - df["ali_from"]) / df["tlen"], 2)
    df["coverage_query"] = round((df["ali_to"] - df["ali_from"]) / df["qlen"], 2)


def _extract_range(threshold):
    # extend regex to allow floats in args directly to set threshold more precisely
    # [+-]?(\d+\.?\d*)|(\.\d+)
    regex = r"(\d+)"
    threshold_range = sorted([float(x) / 100 for x in re.findall(regex, threshold)])
    return threshold_range


def alignments(file):
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
            alignment.append(line)
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


def get_alignment_consensus(file):
    alignments_dict = {}
    for alignment in alignments(file):
        # get the start index of the comsensus sequence.
        # problem: amount of leading whitespaces is dependend on the length of query or target sequence but needs to
        # be exactly calculated because whitespaces in the consensus stand for mismatches of the two aligned sequences
        # Solution: count characters until you hit the first whitespace after hitting letters. Doing it once to get
        # lenght until the name. doing it twice to get characters until the end of the start coordinates.
        temp_index = end_of_column(alignment[2])
        start_index = temp_index + end_of_column(alignment[2][temp_index:]) + 1
        consensus = alignment[1][start_index:].strip("\n")
        query_id, query_start, query_seq, query_end = alignment[0].split()
        target_id, target_start, target_seq, target_end = alignment[2].split()
        key = f"{target_id}-{target_start}-{target_end}"
        perc_ident, perc_sim = calculate_identity_similarity(consensus)
        alignments_dict[key] = {
            "consensus": consensus,
            "target_start": target_start,
            "target_end": target_end,
            "target_seq": target_seq,
            "query_start": query_start,
            "query_end": query_end,
            "query_seq": query_seq,
            "perc_ident": perc_ident,
            "perc_sim": perc_sim,
        }
    return alignments_dict


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
    alignments = results_basepath / "alignments.json"
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


class hmmerResults:
    """Class to hold HMMER search results in a pandas dataframe"""

    def __init__(self, results):
        self.df = results

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, results) -> pd.DataFrame:
        """read the HMMER Domain Table file into a Pandas dataframe"""
        if results.suffix == ".csv":
            self._df = pd.read_csv(results)
        else:
            self._df = pd.read_csv(
                results,
                sep=r"\s+",
                comment="#",
                index_col=False,
                names=[
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
                    "PL",
                    "UP",
                    "biome",
                    "LEN",
                    "CR",
                ],
                dtype={
                    "target_name": str,
                    "target_accession": str,
                    "tlen": int,
                    "query_name": str,
                    "query_accession": str,
                    "qlen": int,
                    "e-value": float,
                    "score": float,
                    "bias": float,
                    "ndom": int,
                    "ndom_of": int,
                    "c-value": float,
                    "i-value": float,
                    "dom_score": float,
                    "dom_bias": float,
                    "hmm_from": int,
                    "hmm_to": int,
                    "ali_from": int,
                    "ali_to": int,
                    "env_from": int,
                    "env_to": int,
                    "acc": float,
                    "description": str,
                },
            )

            def split_description():
                self._df.drop("LEN", axis=1, inplace=True)
                for column in ["PL", "UP", "biome", "CR"]:
                    self._df[column] = self._df[column].apply(lambda x: x.split("=")[1])

            split_description()

            def calculate_coverage():
                self._df["coverage_hit"] = round(
                    (self._df["ali_to"] - self._df["ali_from"])
                    / self._df["tlen"]
                    * 100,
                    2,
                )
                self._df["coverage_query"] = round(
                    (self._df["ali_to"] - self._df["ali_from"])
                    / self._df["qlen"]
                    * 100,
                    2,
                )

            calculate_coverage()

    def save(self, outfile, sep=";", index=False, **kwargs):
        self.df.to_csv(outfile, sep=sep, index=index, **kwargs)
