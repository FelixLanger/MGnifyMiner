#! /usr/bin/env python3

import argparse
from pathlib import Path

from mgyminer.filter import filter, plot_residue_histogram, residue_filter
from mgyminer.phmmer import phmmer
from mgyminer.phyltree import tree


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
        "--coverage",
        type=str,
        required=False,
        metavar="[0-100]",
        help="Filter results by coverage of query sequence. "
        "Threshold range (0-100) percent coverage of query sequence",
    )
    filter_parser.add_argument(
        "--eval",
        type=float,
        required=False,
        metavar="0.001",
        help="Filter by e-value. Threshold for highest e-value displayed",
    )
    filter_parser.add_argument(
        "--sort",
        required=False,
        nargs="+",
        metavar="eval, coverage, similarity, identity",
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
        "tree",
        help="build a phylogenetic tree",
    )
    phylogenetic_tree_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to filter output with sequences for tree building",
    )

    phylogenetic_tree_parser.add_argument(
        "--query",
        type=Path,
        required=True,
        help="Path to query seq",
    )

    phylogenetic_tree_parser.add_argument(
        "--alignment",
        type=Path,
        required=False,
        help="Path to alignment output if desired",
    )
    phylogenetic_tree_parser.add_argument(
        "--output",
        type=Path,
        required=False,
        help="Path/Filename of output tree",
    )

    phylogenetic_tree_parser.set_defaults(func=tree)

    return parser


if __name__ == "__main__":
    main()
