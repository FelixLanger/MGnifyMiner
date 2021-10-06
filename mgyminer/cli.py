#! /usr/bin/env python3

import argparse
from pathlib import Path

from mgyminer.phmmer import phmmer
from mgyminer.phylplot import plot_tree
from mgyminer.phyltree import build_tree
from mgyminer.utils import export_sequences

from mgyminer.filter import (  # isort:skip
    domain_filter,
    filter,
    plot_residue_histogram,
    residue_filter,
)


def main():
    parser = create_parser()
    args = parser.parse_args()
    if "func" in dir(args):
        args.func(args)
    else:
        parser.print_help()


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", "-v", action="version", version="0.0.1", help="show version"
    )
    subparsers = parser.add_subparsers(help="commands")

    # Arguments for sequence search
    phmmer_parser = subparsers.add_parser("phmmer", help="make phmmer search")
    phmmer_parser.add_argument(
        "--query", "-q", type=Path, help="fasta file with query sequence(s)"
    )
    phmmer_parser.add_argument(
        "--target", "-t", type=Path, help="target sequence database to search against"
    )
    phmmer_parser.add_argument("--output", "-o", type=Path, help="output path")
    phmmer_parser.set_defaults(func=phmmer)

    # Arguments for filter step
    filter_parser = subparsers.add_parser(
        "filter", help="filter sequence search results"
    )
    filter_parser.add_argument(
        "--input",
        type=Path,
        metavar="path/to/search_output.txt",
        help="Path to sequence search output file",
    )
    filter_parser.add_argument(
        "--feature",
        type=str,
        required=False,
        metavar="",
        nargs=2,
        help="Filter by any feature e.g. e-value, coverage similarity,..\n"
        "Ranges can be defined like: 1-100\n"
        "Cutoffs can be defined like: <0.5 or >1e-15",
    )

    filter_parser.add_argument(
        "--sort",
        required=False,
        nargs="+",
        metavar="e-value, coverage_hit,coverage_query, similarity, identity",
        help="Sort the output by one or multiple columns.",
    )
    filter_parser.add_argument(
        "--output",
        type=Path,
        metavar="path/to/filter_output.csv",
        help="Path to the desired output file",
    ),
    filter_parser.set_defaults(func=filter)

    residue_parser = subparsers.add_parser(
        "residue", help="filter target proteins by residue features"
    )

    residue_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        metavar="path/to/filter_output.csv",
        help="Path to sequence search output file",
    )
    residue_parser.add_argument(
        "--residue",
        "-r",
        nargs="+",
        action="append",
        metavar="[residue in/exclute AminoAcid1 AA2 ...]",
        help="Filter sequence search hits for specific residues corresponding to the query "
        "sequence. 1st: residue position on query sequence"
        " 2nd: set the filter to include or exclude the aminoacids. "
        " 3rd and following: Aminoacids in single letter code to filter for",
    )
    residue_parser.add_argument(
        "--output",
        type=Path,
        metavar="path/to/filter_output.csv",
        help="Path to the desired output file",
    )
    residue_parser.set_defaults(func=residue_filter)

    residue_checker_parser = subparsers.add_parser(
        "residue_check",
        help="check which aminoacids can be found on"
        " the target sequences corresponding to a"
        " residue in the query",
    )
    residue_checker_parser.add_argument(
        "--residue",
        type=int,
        metavar="155",
        help="Coordinate of the residue in the query sequence",
    )
    residue_checker_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        metavar="path/to/filter_output.csv",
        help="Path to sequence search output file",
    )
    residue_checker_parser.add_argument(
        "--plotwidth",
        type=int,
        metavar="100",
        required=False,
        default=85,
        help="Plot width of the barchart",
    )
    residue_checker_parser.set_defaults(func=plot_residue_histogram)

    phylogenetic_tree_parser = subparsers.add_parser(
        "tree", help="build a phylogenetic tree"
    )
    phylogenetic_tree_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to filter output with sequences for tree building",
    )

    phylogenetic_tree_parser.add_argument(
        "--query", type=Path, required=True, help="Path to query seq"
    )

    phylogenetic_tree_parser.add_argument(
        "--alignment",
        type=Path,
        required=False,
        help="Path to alignment output if desired",
    )
    phylogenetic_tree_parser.add_argument(
        "--output", type=Path, required=False, help="Path/Filename of output tree"
    )

    phylogenetic_tree_parser.set_defaults(func=build_tree)

    tree_vis_parser = subparsers.add_parser(
        "tree_vis", help="visualise phylogenetic tree"
    )
    tree_vis_parser.add_argument(
        "--tree",
        type=Path,
        required=True,
        help="Path to filter output with sequences for tree building",
    )
    tree_vis_parser.add_argument(
        "--filter",
        type=Path,
        required=True,
        help="Path to filter output with sequences for tree building",
    )
    tree_vis_parser.add_argument(
        "--min",
        type=float,
        required=False,
        help="Path to filter output with sequences for tree building",
    )
    tree_vis_parser.add_argument(
        "--max",
        type=float,
        required=False,
        help="Path to filter output with sequences for tree building",
    )
    tree_vis_parser.add_argument(
        "--param",
        type=str,
        required=False,
        help="Path to filter output with sequences for tree building",
    )

    tree_vis_parser.set_defaults(func=plot_tree)

    export_parser = subparsers.add_parser(
        "export", help="export Protein sequences from filter results to FASTA file"
    )
    export_parser.add_argument(
        "--filter",
        type=Path,
        required=True,
        help="Path to filter output of which fasta sequences should be acquired",
    )
    export_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output location for protein sequences FASTA",
    )
    export_parser.set_defaults(func=export_sequences)

    domain_parser = subparsers.add_parser(
        "domain", help="filter target proteins by PFAM domains"
    )
    domain_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        metavar="path/to/filter_output.csv",
        help="Path to sequence search output file",
    )
    domain_parser.add_argument(
        "--arch", "-a", nargs="+", help="Pfams that should be filtered for"
    )
    domain_parser.add_argument(
        "--strict",
        "-s",
        default=False,
        action="store_true",
        help="If strict is set all Pfam domains need to be present, else any of the given domains need to be present",
    )
    domain_parser.add_argument(
        "--output",
        type=Path,
        metavar="path/to/filter_output.csv",
        help="Path to the desired output file",
    )

    domain_parser.set_defaults(func=domain_filter)

    return parser


if __name__ == "__main__":
    main()
