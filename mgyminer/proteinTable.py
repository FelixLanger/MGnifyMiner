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

    def save(self, outfile, sep=";", index=False, **kwargs):
        self.df.to_csv(outfile, sep=sep, index=index, **kwargs)
