import shutil

from mgyminer.cli import create_parser
from mgyminer.utils import biome_str_to_ids, export_sequences, mgyp_to_id, proteinID_to_mgyp, tryfloat
from tests.helpers import get_file_hash


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


def test_export_sequences(tmp_path, seqdb, phmmer_out):
    infile = tmp_path / seqdb.name
    shutil.copy(seqdb, infile)
    outfile = tmp_path / "outfile.fa"
    parser = create_parser()
    command = f"export --seqdb {infile} --filter {phmmer_out} --output {outfile}"
    args = parser.parse_args(command.split())
    export_sequences(args)
    assert get_file_hash(outfile) == "f04c426fbbfbcf3dfac5ec5d8480e74f"


def test_biome_str_to_ids():
    biomes = {
        10: "root:Engineered:Bioremediation",
        9: "root:Engineered:Bioreactor:Continuous culture:Marine sediment inoculum:Wadden Sea-Germany",
        8: "root:Engineered:Bioreactor:Continuous culture:Marine sediment inoculum",
        7: "root:Engineered:Bioreactor:Continuous culture:Marine intertidal flat sediment inoculum:Wadden Sea-Germany",
        6: "root:Engineered:Bioreactor:Continuous culture:Marine intertidal flat sediment inoculum",
        5: "root:Engineered:Bioreactor:Continuous culture",
        4: "root:Engineered:Bioreactor",
        3: "root:Engineered:Biogas plant:Wet fermentation",
        2: "root:Engineered:Biogas plant",
        1: "root:Engineered",
        0: "root",
    }
    assert len(biome_str_to_ids(["root"], biomes)) == 11
    assert sorted(
        biome_str_to_ids(["root:Engineered:Bioreactor:Continuous culture:Marine sediment inoculum"], biomes)
    ) == [8, 9]
    assert sorted(biome_str_to_ids(["root:Engineered:Bioreactor"], biomes)) == [4, 5, 6, 7, 8, 9]
    assert sorted(biome_str_to_ids(["root:Engineered:Bioreactor:Continuous culture:Marine"], biomes)) == [6, 7, 8, 9]
