import json
import random
import string
from unittest import TestCase

from mgyminer.parsers import calculate_identity_similarity, extract_alignments
from tests.conftest import data_dir


def test_extract_alignments():
    with open(data_dir / "alignment.json") as json_file:
        expected_alignment = json.load(json_file)
    alignment = extract_alignments(data_dir / "phmmer_out.txt")
    TestCase().assertDictEqual(expected_alignment, alignment)


def test_calculate_identity_similarity():
    for i in range(10):
        similar_aas = random.randint(0, 200)
        identical_aas = random.randint(0, 200)
        different_aas = random.randint(0, 200)
        digits = random.randint(0, 5)
        length = similar_aas + identical_aas + different_aas
        consensus = (
            random.choices(string.ascii_lowercase, k=identical_aas)
            + ([" "] * different_aas)
            + (["+"] * similar_aas)
        )
        random.shuffle(consensus)
        consensus = "".join(consensus)
        similarity_expected = round(
            ((similar_aas + identical_aas) / length) * 100, digits
        )
        identity_expected = round((identical_aas / length) * 100, digits)
        assert calculate_identity_similarity(consensus, digit=digits) == (
            identity_expected,
            similarity_expected,
        )
