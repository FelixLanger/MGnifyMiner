from hmmer import SeqDB


def phmmer(args):
    """
    run phmmer search of query sequence(s) against sequence database
    :return:
    """
    # manage arguments
    save_dir = args.output.parents[0]
    dom_tbl = save_dir / "dom_tbl.txt"
    tbl = save_dir / "tbl.txt"
    alignment = save_dir / "alignment.sto"

    targetDB = SeqDB(args.target)
    targetDB.phmmer(
        args.query,
        output=args.output,
        tblout=tbl,
        domtblout=dom_tbl,
        alignment=alignment,
        notextw=True,
    )
