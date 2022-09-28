from mgyminer.structure import (
    StructureDownloader,
    filter_msa,
    get_sto_entries,
    remove_entries,
)
from tests.helpers import get_file_hash


def test_get_sto_entries(sto_ali):
    assert get_sto_entries(sto_ali) == [
        "MGYP000329524085/1-292",
        "MGYP000406905322/19-310",
        "MGYP000420419373/1-290",
        "MGYP001583336646/30-318",
        "MGYP001082675080/61-129",
        "MGYP001082675080/145-313",
        "MGYP000754038055/47-132",
        "MGYP000573421630/126-244",
        "MGYP000604501205/1-86",
        "MGYP001394579466/24-120",
        "MGYP000062928162/110-140",
        "MGYP001450139400/31-72",
    ]


def test_remove_entries():
    entries = [
        "MGYP000329524085/1-292",
        "MGYP000406905322/19-310",
        "MGYP000420419373/1-290",
        "MGYP001583336646/30-318",
        "MGYP001082675080/61-129",
        "MGYP001082675080/145-313",
        "MGYP000754038055/47-132",
        "MGYP000573421630/126-244",
        "MGYP000604501205/1-86",
        "MGYP001394579466/24-120",
        "MGYP000062928162/110-140",
        "MGYP001450139400/31-72",
    ]
    cases = [
        {
            "selection": [
                "MGYP000329524085",
                "MGYP000406905322",
                "MGYP000420419373",
                "MGYP001583336646",
                "MGYP001082675080",
            ],
            "expected": [
                "MGYP000754038055/47-132",
                "MGYP000573421630/126-244",
                "MGYP000604501205/1-86",
                "MGYP001394579466/24-120",
                "MGYP000062928162/110-140",
                "MGYP001450139400/31-72",
            ],
        },
        {
            "selection": [
                "MGYP000329524085",
                "MGYP000420419373",
                "MGYP000754038055",
                "MGYP000604501205",
                "MGYP001450139400",
            ],
            "expected": [
                "MGYP000406905322/19-310",
                "MGYP001583336646/30-318",
                "MGYP001082675080/61-129",
                "MGYP001082675080/145-313",
                "MGYP000573421630/126-244",
                "MGYP001394579466/24-120",
                "MGYP000062928162/110-140",
            ],
        },
    ]
    for case in cases:
        assert sorted(remove_entries(case["selection"], entries)) == sorted(
            case["expected"]
        )


def test_filter_msa(sto_ali, tmp_path):
    entries = [
        "MGYP000329524085",
        "MGYP000406905322",
        "MGYP000420419373",
        "MGYP001082675080",
        "MGYP000754038055",
        "MGYP000573421630",
        "MGYP000604501205",
        "MGYP001394579466",
        "MGYP000062928162",
        "MGYP001450139400",
    ]
    outfile = tmp_path / "filtered.sto"
    filter_msa(sto_ali, entries, outfile)
    assert (
        get_file_hash(outfile, ignore_comments=False)
        == "34c39399e55422be4778a3d36f4544c8"
    )


def test_download_alphafold(tmp_path):
    sdl = StructureDownloader()
    outfile = tmp_path / "af.pdb"
    sdl.download_alphafold("AF-A0A452S449-F1", outfile)
    assert (
        get_file_hash(outfile, ignore_comments=True)
        == "1f6d5f9b27428ebceb44df57b9a90709"
    )


def test_download_pdb(tmp_path):
    sdl = StructureDownloader()
    outfile = tmp_path / "pdb.pdb"
    sdl.download_pdb("100D", outfile)
    assert (
        get_file_hash(outfile, ignore_comments=True)
        == "9395d751c49f340536d9f1fc47148981"
    )
