import re
from pathlib import Path
from typing import Tuple, Union


def extract_alignments(hmmer_out: Union[Path, str]) -> dict:
    """
    Takes hmmer standard output file (with notextwidth! option) and creates a dict with alignment
    and similarity and identity metrics
    :param hmmer_out: Path to hmmer output
    :return: alignment dictionary
    """
    alignments_dict = {}
    for alignment in alignments(hmmer_out):
        start, end = _start_end_coordinates(alignment[2])
        consensus = alignment[1][start:end]
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


def calculate_identity_similarity(consensus, round_to=1) -> Tuple[float, float]:
    """
    Calculate sequence similarity and identity values from a hmmer alignment consensus string
    :param consensus: hmmer consensus sequence
    :param round_to: integers after point to keep
    :return: (identity_percentage, similarity_percentage)
    """
    length = len(consensus)
    similar = consensus.count("+")
    mismatch = consensus.count(" ")
    identical = length - mismatch - similar

    percent_identity = round(identical / length * 100, round_to)
    percent_similarity = round((identical + similar) / length * 100, 1)

    return percent_identity, percent_similarity


def _start_end_coordinates(alignment) -> Tuple[int, int]:
    """
    Extract the start and end coordinates of the third hmmer alignment string.
    The alignment string needs to be the target section of the alignment with MGYP ID.
    It removes starting whitespaces, sequence name and start, end coords of the protein.
    :param alignment: alignment string
    :return: (start, end) coordinates of alignment string
    """
    start_pattern = re.compile(r"\s*MGYP\d*\s+\d+\s{1}")
    end_pattern = re.compile(r"\s\d+$")
    alignment_start = start_pattern.match(alignment).end()
    alignment_end = end_pattern.search(alignment).start()
    return alignment_start, alignment_end


def alignments(file: Union[Path, str]):
    """
    Generator for going through the alignments in a HMMER output file with no textwidth
    formatting.
    :param file:
    :return:
    """
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
            alignment.append(line.strip("\n"))
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


def decomment(rows):
    """
    Generator to return a file row by row without # comments
    :param rows:
    :return:
    """
    for row in rows:
        if row.startswith("#"):
            continue
        yield row
