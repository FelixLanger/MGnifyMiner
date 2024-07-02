import os
from typing import Any, Dict, List

import pandas as pd
import psutil
import pyhmmer
from pyhmmer.easel import Alphabet, SequenceFile
from pyhmmer.plan7 import HMMFile

from .fasta import export_sequences
from .proteintable import ProteinTable

COLUMN_NAMES = [
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


def format_number(number: float) -> str:
    if "e" in f"{number}":
        return f"{number:.1e}"
    elif number < 1:
        return str(round(number, 4))
    else:
        return str(round(number, 1))


def calculate_domain_coverage(sequence_length: int, domain: pyhmmer.plan7.Domain, digit: int = 1):
    return round(((domain.alignment.hmm_to - domain.alignment.hmm_from) / sequence_length) * 100, digit)


def calculate_identity(alignment: pyhmmer.plan7.Alignment, digit: int = 1) -> float:
    similar = alignment.identity_sequence.count("+")
    mismatch = alignment.identity_sequence.count(" ")
    length = len(alignment.hmm_sequence)
    identical = length - mismatch - similar
    percent_identity = round(identical / length * 100, digit)
    return percent_identity


def calculate_similarity(alignment: pyhmmer.plan7.Alignment, digit: int = 1) -> float:
    similar = alignment.identity_sequence.count("+")
    mismatch = alignment.identity_sequence.count(" ")
    length = len(alignment.hmm_sequence)
    identical = length - mismatch - similar
    percent_similarity = round((identical + similar) / length * 100, digit)
    return percent_similarity


def process_hit(hit: pyhmmer.plan7.Hit, hits: pyhmmer.plan7.TopHits) -> List[List[str]]:
    hit_results = []
    for domain_idx, domain in enumerate(hit.domains.included, start=1):
        ident = calculate_identity(domain.alignment)
        sim = calculate_similarity(domain.alignment)
        line = [
            hit.name.decode(),
            hit.length,
            hit.best_domain.alignment.hmm_name.decode(),
            hits.query_length,
            format_number(hit.evalue),
            format_number(hit.score),
            format_number(hit.bias),
            domain_idx,
            len(hit.domains.included),
            format_number(domain.c_evalue),
            format_number(domain.i_evalue),
            format_number(domain.score),
            format_number(domain.bias),
            domain.alignment.hmm_from,
            domain.alignment.hmm_to,
            domain.env_from,
            domain.env_to,
            calculate_domain_coverage(hits.query_length, domain),
            calculate_domain_coverage(hit.length, domain),
            sim,
            ident,
        ]
        hit_results.append(line)
    return hit_results


def phmmer(
    db_file: str,
    query_file: str,
    cpus: int = 4,
    memory: float = None,
    max_memory_load: float = 0.8,
    **kwargs: Dict[str, Any],
) -> ProteinTable:
    available_memory = (memory * 1048576) if memory else psutil.virtual_memory().available
    database_size = os.stat(db_file).st_size

    results = []
    alphabet = Alphabet.amino()
    with SequenceFile(db_file, digital=True, alphabet=alphabet) as sequences:
        if database_size < available_memory * max_memory_load:
            sequences = sequences.read_block()
        with SequenceFile(query_file, digital=True, alphabet=alphabet) as queries:
            hits_list = pyhmmer.hmmer.phmmer(queries, sequences, cpus=cpus, **kwargs)
            for hits in hits_list:
                for hit in hits:
                    if hit.reported:
                        results.extend(process_hit(hit, hits))
    return ProteinTable(pd.DataFrame(results, columns=COLUMN_NAMES))


def phmmer_cli(args):
    output_file = args.output
    db_file = args.target
    query_file = args.query
    cpus = args.cpu
    evalue = args.evalue

    hits = phmmer(db_file, query_file, cpus, E=evalue)
    if not args.no_metadata:
        hits = hits.fetch_metadata("bigquery")
    hits.save(output_file)
    if args.fetch_hits:
        export_sequences(db_file, hits.unique_hits, output_file.with_suffix(".faa"))


def hmmsearch(
    seqdb: str,
    hmm: str,
    cpus: int = 4,
    memory: float = None,
    max_memory_load: float = 0.8,
    **kwargs: Dict[str, Any],
) -> ProteinTable:
    available_memory = (memory * 1048576) if memory else psutil.virtual_memory().available
    database_size = os.stat(seqdb).st_size

    results = []
    with SequenceFile(seqdb, digital=True) as sequences:
        if database_size < available_memory * max_memory_load:
            sequences = sequences.read_block()
        with HMMFile(hmm) as hmms:
            if hmms.is_pressed():
                hmms = hmms.optimized_profiles()
            hits_list = pyhmmer.hmmer.hmmsearch(hmms, sequences, cpus=cpus, **kwargs)
            for hits in hits_list:
                for hit in hits:
                    if hit.reported:
                        results.extend(process_hit(hit, hits))
    return ProteinTable(pd.DataFrame(results, columns=COLUMN_NAMES))


def hmmsearch_cli(args):
    output_file = args.output
    db_file = args.target
    query_file = args.query
    cpus = args.cpu
    evalue = args.evalue

    hits = hmmsearch(db_file, query_file, cpus, E=evalue)
    if not args.no_metadata:
        hits = hits.fetch_metadata("bigquery")
    hits.save(output_file)
    if args.fetch_hits:
        export_sequences(db_file, hits.unique_hits, output_file.with_suffix(".faa"))
