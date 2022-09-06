import subprocess

import pandas as pd


def test_cli_phmmer_search(tmp_path, queryseq, seqdb):
    outfile = tmp_path / "outfile.txt"
    name = queryseq.stem
    command = f"MGnifyMiner phmmer --query {queryseq} --target {seqdb} --output {outfile} --keep"
    subprocess.run(command.split())
    for resultfile in [
        f"{name}_dom_tbl.txt",
        f"{name}_hmmer.out",
        f"{name}_tbl.txt",
        f"{name}_alignment.sto",
        "alignment.json",
        outfile,
    ]:
        assert (tmp_path / resultfile).is_file() and (
            tmp_path / "query_alignment.sto"
        ).stat().st_size > 0


def test_cli_sort(tmp_path, phmmer_out):
    outfile = tmp_path / "sorted_results.txt"
    command = f"MGnifyMiner sort --input {phmmer_out} --feature tlen --ascending --output {outfile}"
    subprocess.run(command.split())
    results = pd.read_csv(outfile)
    assert results.iloc[6]["target_name"] == "MGYP000329524085"

    command = (
        f"MGnifyMiner sort --input {phmmer_out} --feature similarity --output {outfile}"
    )
    subprocess.run(command.split())
    results = pd.read_csv(outfile)
    assert results.iloc[8]["target_name"] == "MGYP000604501205"

    command = f"MGnifyMiner sort --input {phmmer_out} --feature e-value identity --ascending --output {outfile}"
    subprocess.run(command.split())
    results = pd.read_csv(outfile)
    assert results.iloc[4]["identity"] == 33.1


def test_cli_filter(tmp_path, phmmer_out):
    # test different number notations and match function
    outfile = tmp_path / "filtered_results.txt"
    # match_cases = [
    #     {
    #         "feature": "tlen",
    #         "value": 127,
    #         "expected_first": "MGYP000604501205",
    #         "nresults": 1,
    #     },
    #     {
    #         "feature": "e-value",
    #         "value": 7.2e-77,
    #         "expected_first": "MGYP001583336646",
    #         "nresults": 1,
    #     },
    #     {
    #         "feature": "FL",
    #         "value": 1,
    #         "expected_first": "MGYP001082675080",
    #         "nresults": 3,
    #     },
    #     {
    #         "feature": "score",
    #         "value": 17.8,
    #         "expected_first": "MGYP000062928162",
    #         "nresults": 2,
    #     },
    # ]
    # for case in match_cases:
    #     command = (
    #         f"MGnifyMiner filter --input {phmmer_out} --feature {case['feature']} --match "
    #         f"{case['value']} --output {outfile}"
    #     )
    #     subprocess.run(command.split())
    #     results = pd.read_csv(outfile)
    #     assert results.iloc[0]["target_name"] == case["expected_first"]
    #     assert len(results) == case["nresults"]

    # test filter thresholds
    command = f"MGnifyMiner filter --input {phmmer_out} --feature tlen --upper 300 --output {outfile}"
    subprocess.run(command.split())
    results = pd.read_csv(outfile)
    assert list(results["target_name"]) == [
        "MGYP000329524085",
        "MGYP000420419373",
        "MGYP000754038055",
        "MGYP000604501205",
        "MGYP001394579466",
        "MGYP000062928162",
        "MGYP000062928162",
        "MGYP001450139400",
    ]
    command = f"MGnifyMiner filter --input {phmmer_out} --feature tlen --lower 300 --output {outfile}"
    subprocess.run(command.split())
    results = pd.read_csv(outfile)
    assert list(results["target_name"]) == [
        "MGYP000406905322",
        "MGYP001583336646",
        "MGYP001082675080",
        "MGYP001082675080",
        "MGYP000573421630",
    ]
    command = (
        f"MGnifyMiner filter --input {phmmer_out} --feature e-value --lower 7.6e-79 "
        f"--upper 5.2e-09 --output {outfile}"
    )
    subprocess.run(command.split())
    results = pd.read_csv(outfile)
    assert list(results["target_name"]) == [
        "MGYP000420419373",
        "MGYP001583336646",
        "MGYP001082675080",
        "MGYP001082675080",
        "MGYP000754038055",
        "MGYP000573421630",
    ]
