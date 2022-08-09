import subprocess


def test_cli_phmmer_search(tmp_path, queryseq, seqdb):
    outfile = tmp_path / "outfile.txt"
    name = queryseq.stem
    subprocess.run(
        [
            "MGnifyMiner",
            "phmmer",
            "--query",
            queryseq,
            "--target",
            seqdb,
            "--output",
            outfile,
            "--keep",
        ]
    )
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
