import tempfile

import pandas as pd

from mgyminer.phyltree import esl_sfetcher


def export_sequences(args):
    """
    Export sequences from filters to FASTA format
    :param results:
    :return:
    """
    fetcher = esl_sfetcher()
    results = pd.read_csv(args.filter)
    with tempfile.NamedTemporaryFile() as temp:
        results["target_name"].to_csv(temp.name, index=False, header=False)
        fetcher.run("testSeqDB.fa", temp.name, args.output, args=["-f"])
