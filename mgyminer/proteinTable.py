from pathlib import Path
from typing import Union

import pandas as pd
from pandas import DataFrame


class proteinTable:
    """
    Class to hold a list of proteins (from a protein search against the MGnify protein database.
    Central object to perform filters on sequence search results
    """

    def __init__(self, results: Union[Path, str]):
        self.df = results

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, results) -> DataFrame:
        """read the HMMER Domain Table file into a Pandas dataframe"""
        if isinstance(results, str):
            results = Path(results)

        if isinstance(results, DataFrame):
            self._df = results

        elif isinstance(results, Path):
            self._df = pd.read_csv(results)
        else:
            self._df = pd.DataFrame()

    #         else:
    #             self._df = pd.read_csv(
    #                 results,
    #                 sep=r"\s+",
    #                 comment="#",
    #                 index_col=False,
    #                 names=[
    #                     "target_name",
    #                     "target_accession",
    #                     "tlen",
    #                     "query_name",
    #                     "query_accession",
    #                     "qlen",
    #                     "e-value",
    #                     "score",
    #                     "bias",
    #                     "ndom",
    #                     "ndom_of",
    #                     "c-value",
    #                     "i-value",
    #                     "dom_score",
    #                     "dom_bias",
    #                     "hmm_from",
    #                     "hmm_to",
    #                     "ali_from",
    #                     "ali_to",
    #                     "env_from",
    #                     "env_to",
    #                     "acc",
    #                     "PL",
    #                     "UP",
    #                     "biome",
    #                     "LEN",
    #                     "CR",
    #                 ],
    #                 dtype={
    #                     "target_name": str,
    #                     "target_accession": str,
    #                     "tlen": int,
    #                     "query_name": str,
    #                     "query_accession": str,
    #                     "qlen": int,
    #                     "e-value": float,
    #                     "score": float,
    #                     "bias": float,
    #                     "ndom": int,
    #                     "ndom_of": int,
    #                     "c-value": float,
    #                     "i-value": float,
    #                     "dom_score": float,
    #                     "dom_bias": float,
    #                     "hmm_from": int,
    #                     "hmm_to": int,
    #                     "ali_from": int,
    #                     "ali_to": int,
    #                     "env_from": int,
    #                     "env_to": int,
    #                     "acc": float,
    #                     "description": str,
    #                 },
    #             )
    #
    #             def split_description():
    #                 self._df.drop("LEN", axis=1, inplace=True)
    #                 for column in ["PL", "UP", "biome", "CR"]:
    #                     self._df[column] = self._df[column].apply(lambda x: x.split("=")[1])
    #
    #             split_description()
    #
    #             def calculate_coverage():
    #                 self._df["coverage_hit"] = round(
    #                     (self._df["ali_to"] - self._df["ali_from"])
    #                     / self._df["tlen"]
    #                     * 100,
    #                     2,
    #                 )
    #                 self._df["coverage_query"] = round(
    #                     (self._df["ali_to"] - self._df["ali_from"])
    #                     / self._df["qlen"]
    #                     * 100,
    #                     2,
    #                 )
    #
    #             calculate_coverage()
    #
    # @property
    # def alignment_metrics(self):
    #     if ["coverage_hit", "coverage_query", "similarity", "identity"] in self.df.columns:
    #         pass
    #
    #
    # def save(self, outfile, sep=";", index=False, **kwargs):
    #     self.df.to_csv(outfile, sep=sep, index=index, **kwargs)
