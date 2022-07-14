import json
from unittest import TestCase

from mgyminer.parsers import extract_alignments
from tests.fixtures import data_dir


def test_extract_alignments():
    with open(data_dir / "alignment.json") as json_file:
        expected_alignment = json.load(json_file)
    alignment = extract_alignments(data_dir / "phmmer_out.txt")
    TestCase().assertDictEqual(expected_alignment, alignment)
