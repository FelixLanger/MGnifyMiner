import os

import pandas as pd
import psutil
import pyhmmer
from pyhmmer.easel import Alphabet, SequenceFile

from .proteintable import ProteinTable


def custom_round(number):
    if "e" in f"{number}":
        return f"{number:.1e}"
    else:
        return str(round(number, 1))


def calculate_query_coverage(query_length, domain):
    return round(((domain.alignment.hmm_to - domain.alignment.hmm_from) / query_length) * 100)


def calculate_target_coverage(target_length, domain):
    return round(((domain.alignment.hmm_to - domain.alignment.hmm_from) / target_length) * 100)


def calculate_similarity(alignment, digit):
    similar = alignment.identity_sequence.count("+")
    mismatch = alignment.identity_sequence.count(" ")
    length = len(alignment.hmm_sequence)
    identical = length - mismatch - similar
    percent_identity = round(identical / length * 100, digit)
    percent_similarity = round((identical + similar) / length * 100, digit)
    return percent_identity, percent_similarity


def phmmer(db_file, query_file, cpus=4, memory=None):
    MAX_MEMORY_LOAD = 0.80
    available_memory = (memory * 1048576) if memory else psutil.virtual_memory().available
    database_size = os.stat(db_file).st_size

    results = []
    column_names = [
        "target_name",
        "tlen",
        "query_name",
        "qlen",
        "e-value",
        "score",
        "bias",
        "ndom",
        "ndom_of",
        "c-value",
        "i-value",
        "dom_score",
        "dom_bias",
        "hmm_from",
        "hmm_to",
        "env_from",
        "env_to",
        "coverage_query",
        "coverage_hit",
        "similarity",
        "identity",
    ]

    alphabet = Alphabet.amino()
    with SequenceFile(db_file, digital=True, alphabet=alphabet) as sequences:
        if database_size < available_memory * MAX_MEMORY_LOAD:
            sequences = sequences.read_block()
        with SequenceFile(query_file, digital=True, alphabet=alphabet) as queries:
            hits_list = pyhmmer.hmmer.phmmer(queries, sequences, cpus=cpus)
            for hits in hits_list:
                for hit in hits:
                    if hit.reported:
                        n_doms_of = len(hit.domains.included)
                        n_dom = 0
                        for domain in hit.domains.included:
                            n_dom += 1
                            ident, sim = calculate_similarity(domain.alignment, 1)
                            line = [
                                hit.name.decode(),
                                hit.length,
                                hit.best_domain.alignment.hmm_name.decode(),
                                hits.query_length,
                                custom_round(hit.evalue),
                                custom_round(hit.score),
                                custom_round(hit.bias),
                                n_dom,
                                n_doms_of,
                                custom_round(domain.c_evalue),
                                custom_round(domain.i_evalue),
                                custom_round(domain.score),
                                custom_round(domain.bias),
                                domain.alignment.hmm_from,
                                domain.alignment.hmm_to,
                                domain.env_from,
                                domain.env_to,
                                calculate_query_coverage(hits.query_length, domain),
                                calculate_target_coverage(hit.length, domain),
                                sim,
                                ident,
                            ]
                            results.append(line)
    return ProteinTable(pd.DataFrame(results, columns=column_names))


def phmmer_cli(args):
    output_file = args.output
    db_file = args.target
    query_file = args.query
    cpus = args.cpu

    hits = phmmer(db_file, query_file, cpus)
    hits.save("test_diff")
    hits = hits.fetch_metadata("bigquery")
    hits.save(output_file)
