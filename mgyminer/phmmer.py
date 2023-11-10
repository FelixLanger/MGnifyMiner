import json
import logging
import tempfile
from pathlib import Path

from mgyminer.parsers import extract_alignments, parse_hmmer_domtable
from mgyminer.proteinTable import ProteinTableVisualiser, proteinTable
from mgyminer.wrappers.hmmer import PHmmer


def phmmer(args) -> None:
    phmmer = PHmmer(args.cpu)
    phmmer.verbose = True
    query_name = args.query.stem
    output_file = args.output
    if args.keep is True:
        save_dir = args.output.parents[0]
    else:
        tempdir = tempfile.TemporaryDirectory()
        save_dir = Path(tempdir.name)

    hmmer_out = save_dir / f"{query_name}_hmmer.out"
    dom_tbl = save_dir / f"{query_name}_dom_tbl.txt"
    tbl = save_dir / f"{query_name}_tbl.txt"
    alignment = save_dir / f"{query_name}_alignment.sto"
    phmmer.run(
        args.query.resolve(),
        args.target.resolve(),
        hmmer_out,
        domtblout=dom_tbl,
        tblout=tbl,
        alignment=alignment,
    )
    logging.info("running phmmer finished")
    results = parse_hmmer_domtable(dom_tbl)
    alignments = extract_alignments(hmmer_out)
    with open(save_dir / "alignment.json", "w") as fout:
        json.dump(alignments, fout, indent=4, sort_keys=True)

    results["similarity"] = results.apply(
        lambda x: alignments["-".join([x.target_name, str(x.ali_from), str(x.ali_to)])][
            "perc_sim"
        ],
        axis=1,
    )
    results["identity"] = results.apply(
        lambda x: alignments["-".join([x.target_name, str(x.ali_from), str(x.ali_to)])][
            "perc_ident"
        ],
        axis=1,
    )
    results = proteinTable(results)
    results.fetch_metadata(database="bigquery")
    results.save(output_file, index=False)

    if args.dashboard:
        dashboard = ProteinTableVisualiser(results)
        dashboard.save(save_dir / f"{query_name}_dashboard.html")
