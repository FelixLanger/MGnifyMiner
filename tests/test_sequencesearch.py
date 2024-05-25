from mgyminer.sequencesearch import (
    calculate_domain_coverage,
    calculate_identity,
    calculate_similarity,
    format_number,
    phmmer,
)


def test_format_number():
    assert format_number(9.000) == "9.0"
    assert format_number(1.2345) == "1.2"
    assert format_number(1.2345e-10) == "1.2e-10"


def test_calculate_domain_coverage():
    class DomainMock:
        def __init__(self, hmm_from, hmm_to):
            self.alignment = type("AlignmentMock", (), {"hmm_from": hmm_from, "hmm_to": hmm_to})

    domain = DomainMock(10, 20)
    assert calculate_domain_coverage(100, domain) == 10
    domain = DomainMock(10, 21)
    assert calculate_domain_coverage(200, domain) == 5.5


def test_calculate_similarity():
    class AlignmentMock:
        def __init__(self, hmm_sequence, identity_sequence):
            self.hmm_sequence = hmm_sequence
            self.identity_sequence = identity_sequence

    alignment = AlignmentMock("mmmmmmmmmm", "mmmmm     ")
    assert calculate_similarity(alignment, 1) == 50
    alignment = AlignmentMock("mmmmmmmmmm", "m m m m + ")
    assert calculate_similarity(alignment, 1) == 50
    alignment = AlignmentMock("asdfddasef", " sd+d asef")
    assert calculate_similarity(alignment, 2) == 80.0


def test_calculate_identity():
    class AlignmentMock:
        def __init__(self, hmm_sequence, identity_sequence):
            self.hmm_sequence = hmm_sequence
            self.identity_sequence = identity_sequence

    alignment = AlignmentMock("mmmmmmmmmm", "mmmmm     ")
    assert calculate_identity(alignment, 1) == 50
    alignment = AlignmentMock("mmmmmmmmmm", "m m m m + ")
    assert calculate_identity(alignment, 1) == 40
    alignment = AlignmentMock("asdfddasef", " sd+d asef")
    assert calculate_identity(alignment, 2) == 70.0


def test_phmmer(seqdb, queryseq):
    result = phmmer(seqdb, queryseq)
    assert result.iloc[1]["target_name"] == "MGYP000406905322"
    assert result.iloc[2]["e-value"] == "1.1e-78"
    assert result.iloc[5]["ndom"] == 2
    assert len(result) == 12
