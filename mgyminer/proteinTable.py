import re
from pathlib import Path
from typing import Union

import numpy as np
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
    def df(self, results: Union[DataFrame, str, Path]) -> None:
        """read the HMMER Domain Table file into a Pandas dataframe"""
        if isinstance(results, str):
            results = Path(results)

        if isinstance(results, DataFrame):
            self._df = results
        elif isinstance(results, Path):
            self._df = pd.read_csv(results)
        else:
            # TODO Think about if empty protein tables are allowed
            raise NotImplementedError
        self._set_columntypes()

    def _set_columntypes(self):
        self.df.astype(
            dtype={
                "target_name": str,
                "target_accession": str,
                "tlen": int,
                "query_name": str,
                "query_accession": str,
                "qlen": int,
                "e-value": np.object_,
                "score": np.object_,
                "bias": np.object_,
                "ndom": int,
                "ndom_of": int,
                "c-value": np.object_,
                "i-value": np.object_,
                "dom_score": np.object_,
                "dom_bias": np.object_,
                "hmm_from": int,
                "hmm_to": int,
                "ali_from": int,
                "ali_to": int,
                "env_from": int,
                "env_to": int,
                "acc": np.object_,
                "UP": int,
                "biome": str,
                "CR": int,
                "coverage_hit": np.object_,
                "coverage_query": np.object_,
                "similarity": np.object_,
                "identity": np.object_,
            }
        )

    def sort(self, by: Union[str, list], ascending: bool = False):
        """
        General method to sort protein table by column values
        :param by:
        :param ascending:
        :return:
        """
        if not isinstance(by, list):
            by = [by]
        by = self._to_columnNames(by)
        by.extend(["target_name", "ndom"])
        # Set orientation according to setting, but always sort ndom ascending to keep domain order
        orientation = [ascending if _ != "ndom" else True for _ in by]
        self.df = self.df.sort_values(by=by, ascending=orientation)

    def _to_columnNames(self, names: Union[str, list]) -> list:
        """
        method to remap inputs to the corresponding column names
        :param names:
        :return:
        """
        if not isinstance(names, list):
            names = [names]
        mapping = {colname: colname for colname in self.df.columns}
        addins = {"eval": "score", "e-value": "score", "evalue": "score"}
        mapping = {**mapping, **addins}
        return list(map(mapping.get, names))

    def filter(self, by, value):
        span = re.match(r"(\d+)-(\d+)", value)
        thresh = re.match(r"(\d+)-(\d+)", value)
        if thresh:
            mod, v = thresh.groups()
            if mod == "<":
                self.df = self.df[self.df["e-value"] <= int(v)]
            elif mod == ">":
                self.df = self.df[self.df["e-value"] >= int(v)]

        elif span:
            x, y = span.groups()
            self.df = self.df[self.df[by].between(int(x), int(y))]

        else:
            self.df = self.df[self.df["e-value"] <= int(value)]

    def save(self, outfile, sep=",", index=False, **kwargs):
        """
        save protein table to output (csv) fileS
        :param outfile:
        :param sep:
        :param index:
        :param kwargs:
        :return:
        """
        self.df.to_csv(outfile, sep=sep, index=index, **kwargs)
