import json

from hmmer import SeqDB

from mgyminer.parsers import extract_alignments, parse_hmmer_domtable
from mgyminer.proteinTable import proteinTable


def phmmer(args) -> None:
    """
    run phmmer search of query sequence(s) against sequence database
    :return:
    """
    # manage arguments
    query_name = args.query.stem
    output_file = args.output
    save_dir = args.output.parents[0]
    hmmer_out = save_dir / f"{query_name}_hmmer.out"
    dom_tbl = save_dir / f"{query_name}_dom_tbl.txt"
    tbl = save_dir / f"{query_name}_tbl.txt"
    alignment = save_dir / f"{query_name}_alignment.sto"

    targetDB = SeqDB(args.target)
    targetDB.phmmer(
        args.query,
        output=hmmer_out,
        tblout=tbl,
        domtblout=dom_tbl,
        alignment=alignment,
        notextw=True,
    )

    # Generate proteinTable and alignment json
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
    results.save(output_file)
