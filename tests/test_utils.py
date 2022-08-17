from mgyminer.utils import mgyp_to_id, proteinID_to_mgyp, tryfloat


def test_mgyp_to_id():
    cases = [
        ("MGYP000420419373", "420419373"),
        ("MGYP123121231555", "123121231555"),
        ("MGYP000000000001", "1"),
    ]
    for case in cases:
        assert case[1] == mgyp_to_id(case[0])


def test_protein_id_to_mgyp():
    cases = [
        ("MGYP000420419373", "420419373"),
        ("MGYP123121231555", "123121231555"),
        ("MGYP000000000001", "1"),
        ("MGYP000420419373", 420419373),
        ("MGYP123121231555", 123121231555),
        ("MGYP000000000001", 1),
    ]
    for case in cases:
        assert proteinID_to_mgyp(case[1]) == case[0]


def test_tryfloat():
    cases = [("1e-5", 0.00001), ("notafloat", "notafloat"), ("1", 1), ("1E2", 100)]
    for case in cases:
        assert tryfloat(case[0]) == case[1]


# def test_export_sequences():
#     from mgyminer.cli import create_parser
#     parser = create_parser()
#
