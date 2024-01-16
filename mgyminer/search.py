from abc import ABC, abstractmethod
import pyhmmer
import psutil
import os


class HomologySearch(ABC):
    @abstractmethod
    def search_protein(self, query, targetdb):
        """
        Performs a homology search of the query against a targetdb.
        Must return a ProteinTable object.
        """
        pass


class PhmmerSearch(HomologySearch):
    def search_protein(self, query, target):
        available_memory = psutil.virtual_memory().available
        database_size = os.stat(target).st_size

        MAX_MEMORY_LOAD = 0.8

        alphabet = pyhmmer.easel.Alphabet.amino()

        results = []
        with pyhmmer.easel.SequenceFile(
            target, digital=True, alphabet=alphabet
        ) as sequences:
            # pre-load the database if it is small enough to fit in memory
            if database_size < available_memory * MAX_MEMORY_LOAD:
                sequences = sequences.read_block()
            with pyhmmer.easel.SequenceFile(
                query, digital=True, alphabet=alphabet
            ) as queries:
                hits_list = pyhmmer.phmmer(queries, sequences)
                for search in hits_list:
                    query_name = search.query_name
                    for hit in search:
                        if hit.reported:
                            target_name = hit.name.decode()
                            eval = hit.evalue
                            bias = hit.bias
                            score = hit.score
                            for domain in hit.domains:
                                print(domain)
                        results.append(target_name, query_name, eval, bias, score)


# [target_name,target_accession,tlen,query_name,query_accession,qlen,e-value,score,bias,ndom,ndom_of,c-value,i-value,dom_score,dom_bias,hmm_from,hmm_to,ali_from,ali_to,env_from,env_to,acc,CR,FL,coverage_hit,coverage_query,similarity,identity]


ph = PhmmerSearch()
ph.search_protein(
    "../tests/data/sequence_files/query.fa", "../tests/data/sequence_files/seqdb.fa"
)
