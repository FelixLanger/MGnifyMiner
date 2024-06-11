import pandas as pd
from helpers import calculate_text_md5
from pandas.testing import assert_series_equal

from mgyminer.proteintable import ProteinTable


def test_initialising_from_hmmer_results(phmmer_out):
    df = pd.read_csv(phmmer_out)
    protein_table = ProteinTable(df)
    assert protein_table.shape[0] == 13
    assert protein_table.shape[1] == 28

    assert protein_table["target_name"][0] == "MGYP000329524085"
    assert protein_table["e-value"][9] == 7.4e-9

    assert protein_table["e-value"].dtype == "float64"
    assert protein_table["qlen"].dtype == "int64"


def test_initialising_with_metadata(results_metadata):
    protein_table = ProteinTable(results_metadata)
    assert protein_table.shape[0] == 35
    assert protein_table.shape[1] == 30

    assert protein_table["target_name"][12] == "MGYP002783763015"
    assert protein_table["e-value"][9] == 1.8e-49

    assert protein_table["e-value"].dtype == "float64"
    assert protein_table["qlen"].dtype == "int64"
    assert isinstance(protein_table["complete"][0], list)
    assert isinstance(protein_table["complete"][0][0], bool)
    assert isinstance(protein_table["biomes"][1], list)
    assert protein_table["biomes"][1][0] == 171
    assert len(protein_table["assemblies"][5]) == 6
    assert protein_table["assemblies"][8][2] == "ERZ781395"


def test_n_unique_hit(results_metadata):
    protein_table = ProteinTable(results_metadata)
    assert protein_table.n_unique_hits == 31


def test_pick_min_max(results_metadata):
    protein_table = ProteinTable(results_metadata)
    filtered = protein_table.pick({"e-value": {"max": 1e-50}})
    assert len(filtered) == 7
    assert list(filtered.unique_hits) == [
        "MGYP000052290578",
        "MGYP000574657128",
        "MGYP000238484700",
    ]

    filtered = protein_table.pick({"tlen": {"min": 1000}})
    assert len(filtered) == 9

    filtered = protein_table.pick({"score": {"min": 180, "max": 310}})
    assert len(filtered) == 8


def test_filter_nested_columns_numeric(results_metadata):
    protein_table = ProteinTable(results_metadata)
    filtered = protein_table.pick({"biomes": [133, 106, 4, 62]})
    assert len(filtered) == 13


def test_filter_nested_columns_str(results_metadata):
    protein_table = ProteinTable(results_metadata)
    filtered = protein_table.pick(
        {
            "biomes": [
                "root:Environmental:Aquatic:Marine:Brackish",
                "root:Environmental:Aquatic:Freshwater:Lentic",
                "root:Engineered:Bioreactor",
                "root:Engineered:Wastewater",
            ]
        }
    )
    assert len(filtered) == 13


def test_filter_list(results_metadata):
    protein_table = ProteinTable(results_metadata)
    filtered = protein_table.pick({"assemblies": ["ERZ650666"]})
    assert filtered.shape == (5, 30)
    assert filtered.columns.to_list() == protein_table.columns.to_list()
    assert filtered.unique_hits.tolist() == ["MGYP000574657128", "MGYP000238484700"]

    filtered = protein_table.pick({"assemblies": ["ERZ650666", "ERZ795000"]})
    assert filtered.shape == (6, 30)
    assert filtered.columns.to_list() == protein_table.columns.to_list()
    assert filtered.unique_hits.tolist() == ["MGYP000574657128", "MGYP000238484700", "MGYP001204071612"]

    filtered = protein_table.pick({"biomes": [133, 106, 4, 62]})
    assert filtered.shape == (13, 30)
    assert filtered.columns.to_list() == protein_table.columns.to_list()
    assert set(filtered.unique_hits) == {
        "MGYP000574657128",
        "MGYP001204071612",
        "MGYP000238484700",
        "MGYP000265027127",
        "MGYP001150985993",
        "MGYP002619593550",
        "MGYP006148577279",
        "MGYP006170126771",
        "MGYP000849755858",
        "MGYP000983906205",
    }

    # # All proteins should have at least "root:" as biome
    filtered = protein_table.pick({"biomes": ["root"]})
    assert filtered.shape == (35, 30)
    assert filtered.columns.to_list() == protein_table.columns.to_list()
    assert_series_equal(filtered["biomes"], protein_table["biomes"])

    filtered = protein_table.pick({"truncation": ["11"]})
    assert filtered.shape == (9, 30)
    assert filtered.columns.to_list() == protein_table.columns.to_list()

    filtered = protein_table.pick({"complete": [True]})
    assert filtered.shape == (13, 30)
    assert filtered.columns.to_list() == protein_table.columns.to_list()


def test_filter_combination(results_metadata):
    protein_table = ProteinTable(results_metadata)
    filtered = protein_table.pick(
        {
            "tlen": {"min": 500, "max": 1750},
            "assemblies": ["ERZ511468", "ERZ1758439", "ERZ781399", "ERZ795000"],
        }
    )
    assert len(filtered) == 5
    filtered = protein_table.pick({"biomes": ["root:Environmental:Aquatic"], "tlen": {"min": 500, "max": 1000}})
    assert len(filtered) == 10


def test_save(results_metadata, tmp_path):
    outfile = tmp_path / "results.csv"
    in_hash = calculate_text_md5(results_metadata)
    protein_table = ProteinTable(results_metadata)
    protein_table.save(outfile)
    out_hash = calculate_text_md5(outfile)
    assert in_hash == out_hash


def test_value_counts_nested():
    df = ProteinTable(pd.DataFrame({"lists_column": [[1, 2, 3], [2, 3, 4], [5]]}))
    assert df.value_counts_nested("lists_column") == 5

    df = ProteinTable(pd.DataFrame({"lists_column": [[1, 2, 3], [2, 3], [], [4]]}))
    assert df.value_counts_nested("lists_column") == 4

    df = ProteinTable(pd.DataFrame({"lists_column": [[1, 2, 3], None, [], [4]]}))
    assert df.value_counts_nested("lists_column") == 4
