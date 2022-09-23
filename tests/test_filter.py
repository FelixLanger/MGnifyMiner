from collections import Counter


def test_overlaps_at(alignmt):
    cases = [
        {
            "coordinate": 50,
            "expected": [
                "MGYP000062928162-5-77",
                "MGYP000329524085-1-292",
                "MGYP000406905322-19-310",
                "MGYP000420419373-1-290",
                "MGYP001394579466-24-120",
                "MGYP001583336646-30-318",
            ],
        },
        {
            "coordinate": 280,
            "expected": [
                "MGYP000329524085-1-292",
                "MGYP000406905322-19-310",
                "MGYP000420419373-1-290",
                "MGYP001082675080-145-313",
                "MGYP001583336646-30-318",
            ],
        },
        {"coordinate": 300, "expected": []},
    ]

    for case in cases:
        match_entries = [
            entry for entry, data in alignmt.overlaps_at(case["coordinate"])
        ]
        assert match_entries == case["expected"]


def test_match_residue(alignmt):
    cases = [
        {
            "coordinate": 1,
            "aminoacid": "M",
            "expected": [
                "MGYP000329524085-1-292",
                "MGYP000406905322-19-310",
                "MGYP000420419373-1-290",
            ],
        },
        {
            "coordinate": 130,
            "aminoacid": "E",
            "expected": [
                "MGYP000329524085-1-292",
                "MGYP000406905322-19-310",
                "MGYP001082675080-145-313",
                "MGYP001583336646-30-318",
            ],
        },
        {
            "coordinate": 130,
            "aminoacid": ["E", "T"],
            "expected": [
                "MGYP000329524085-1-292",
                "MGYP000406905322-19-310",
                "MGYP000573421630-126-244",
                "MGYP001082675080-145-313",
                "MGYP001082675080-61-129",
                "MGYP001583336646-30-318",
            ],
        },
    ]
    for case in cases:
        matches = alignmt.match_residue(case["coordinate"], case["aminoacid"])
        assert list(matches.keys()) == case["expected"]


def test_match_query(alignmt):
    cases = [
        {
            "coordinate": 140,
            "expected": [
                "MGYP000329524085-1-292",
                "MGYP000406905322-19-310",
            ],
        },
        {
            "coordinate": 179,
            "expected": [
                "MGYP000329524085-1-292",
                "MGYP000406905322-19-310",
                "MGYP000420419373-1-290",
                "MGYP001583336646-30-318",
            ],
        },
        {
            "coordinate": 200,
            "expected": [
                "MGYP000329524085-1-292",
                "MGYP000406905322-19-310",
                "MGYP001082675080-145-313",
            ],
        },
    ]
    for case in cases:
        matches = alignmt.match_query(case["coordinate"])
        assert list(matches.keys()) == case["expected"]


def test_residue_distribution(alignmt):
    cases = [
        {
            "coordinate": 200,
            "expected": Counter(["T", "T", "H", "P", "Y", "H", "T", "C"]),
        },
        {"coordinate": 1, "expected": Counter(["M", "M", "M"])},
        {"coordinate": 180, "expected": Counter(["I", "I", "I", "L", "V", "I", "I"])},
    ]
    for case in cases:
        assert alignmt.residue_distribution(case["coordinate"]) == case["expected"]


def test_ids(alignmt):
    assert set(alignmt.ids()) == {
        "MGYP000329524085",
        "MGYP000406905322",
        "MGYP000420419373",
        "MGYP001583336646",
        "MGYP001082675080",
        "MGYP000754038055",
        "MGYP000573421630",
        "MGYP000604501205",
        "MGYP001394579466",
        "MGYP000062928162",
        "MGYP001450139400",
    }


def test_corresponding_aa(alignmt):
    cases = [
        {"coordinate": 52, "key": "MGYP000062928162-5-77", "expected": "I"},
        {"coordinate": 10, "key": "MGYP000329524085-1-292", "expected": "I"},
        {"coordinate": 140, "key": "MGYP001082675080-145-313", "expected": "N"},
    ]
    for case in cases:
        assert (
            alignmt.corresponding_aa(case["key"], case["coordinate"])
            == case["expected"]
        )
