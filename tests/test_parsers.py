import json
from unittest import TestCase

from mgyminer.parsers import extract_alignments


def test_extract_alignments():
    with open("data/alignment.json") as json_file:
        expected_alignment = json.load(json_file)
    alignment = extract_alignments("./data/phmmer_out.txt")
    TestCase().assertDictEqual(expected_alignment, alignment)
