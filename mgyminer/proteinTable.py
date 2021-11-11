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
        if isinstance(results, str):
            results = Path(results)

        if isinstance(results, DataFrame):
            self.df = results
        elif isinstance(results, Path):
            self.df = pd.read_csv(
                results, dtype={"biome": str, "PL": str, "UP": str, "CR": str}
            )
        else:
            raise TypeError(
                "proteinTable must be initialised with DataFrame or Path to csv file"
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
        # TODO remove conversion feature, or redo it in a way that we first check if input is in mapping or column
        # and if not then raise Error
        # by = self._to_columnNames(by)

        if not set(by).issubset(set(self.df.columns)):
            not_in_df = set(by) - set(set(self.df.columns))
            raise KeyError(f"{not_in_df} not found in results table")

        by.extend(["target_name", "ndom"])
        # Set orientation according to setting, but always sort ndom ascending to keep domain order
        orientation = [ascending if _ != "ndom" else True for _ in by]
        return proteinTable(self.df.sort_values(by=by, ascending=orientation))

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
        """
        Filter proteinTable by any column value
        :param by: column name
        :param value: value to filter for (threshold with <,> or range with x-y)
        :return: filtered Dataframe
        """
        if by not in self.df.columns:
            raise ValueError(
                f"{by} not in Table columns. Choose one of: {' '.join(self.df.columns)}"
            )

        if np.issubdtype(self.df[by].dtype, np.number):
            span = re.match(r"(\d+)-(\d+)", value)
            thresh = re.match(r"([><])(.+)", value)
            if thresh:
                mod, v = thresh.groups()
                v = np.float(v)
                if mod == "<":
                    return proteinTable(self.df[self.df[by] <= v])
                elif mod == ">":
                    return proteinTable(self.df[self.df[by] >= v])

            elif span:
                x, y = span.groups()
                return proteinTable(
                    self.df[self.df[by].between(np.float(x), np.float(y))]
                )

            else:
                return proteinTable(self.df[self.df[by] <= np.float(value)])
        else:
            return proteinTable(self.df[self.df[by] == value])

    def biome(self, biome):
        """
        Filter proteins by biome
        :param biome:
        :return:
        """
        biomes = [
            "engineered",
            "aquatic",
            "marine",
            "freshwater",
            "soil",
            "clay",
            "shrubland",
            "plants",
            "human",
            "human_digestive_system",
            "human_not_digestive_system",
            "animal",
            "other",
        ]
        if biome not in biomes:
            raise ValueError(f"{biome} not in available biomes. Select one of {biomes}")
        temp = pd.DataFrame(
            self.df["biome"].apply(lambda x: list(x)).to_list(), columns=biomes
        )
        index = temp[temp[biome] == "1"].index
        return proteinTable(self.df[self.df.index.isin(index)])

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
