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
    assert results.iloc[6]["target_name"] == "MGYP000406905322"

    command = (
        f"MGnifyMiner sort --input {phmmer_out} --feature similarity --output {outfile}"
    )
    subprocess.run(command.split())
    results = pd.read_csv(outfile)
    assert results.iloc[8]["target_name"] == "MGYP001394579466"

    command = f"MGnifyMiner sort --input {phmmer_out} --feature e-value identity --ascending --output {outfile}"
    subprocess.run(command.split())
    results = pd.read_csv(outfile)
    assert results.iloc[7]["identity"] == 24.7
