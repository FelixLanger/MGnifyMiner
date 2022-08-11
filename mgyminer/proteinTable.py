from collections import Counter
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
import plotly.graph_objs as go
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
        :param by: columnname or list of columns to sort proteinTable
        :param ascending: bool if sort should be ascending, default False
        :return: sorted proteinTable
        """
        if not isinstance(by, list):
            by = [by]

        if not set(by).issubset(set(self.df.columns)):
            not_in_df = set(by) - set(set(self.df.columns))
            raise KeyError(f"{not_in_df} not found in proteinTable columns")

        by.extend(["target_name", "ndom"])
        # Set orientation according to arguments, but always sort ndom ascending to keep domain order
        orientation = [ascending if _ != "ndom" else True for _ in by]
        return proteinTable(self.df.sort_values(by=by, ascending=orientation))

    def threshold(self, column, greater=np.NINF, less=np.PINF):
        """
        Filter proteinTable based on value or value range in column.
        Set only one threshold or multiple to define range.
        :param column: column name
        :param less: threshold where column values should be less than (<)
        :param greater: threshold where column values should be greater than (>)
        :return: filtered Dataframe
        """
        if column not in self.df.columns:
            raise ValueError(
                f"{column} not in Table columns. Choose one of: {' '.join(self.df.columns)}"
            )
        elif not np.issubdtype(self.df[column].dtype, np.number):
            raise ValueError(f"{column} column is not numeric")

        return proteinTable(
            self.df[(self.df["tlen"] >= greater) & (self.df["tlen"] <= less)]
        )

    def match(self, column, value):
        """
        Filter rows in proteinTable that have value in column
        :param column: column name
        :param value: value to filter for in column
        :return: filtered Dataframe
        """
        if column not in self.df.columns:
            raise ValueError(
                f"{column} not in Table columns. Choose one of: {' '.join(self.df.columns)}"
            )
        return proteinTable(self.df[self.df[column] == value])

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


class ProteinTableVisualiser:
    def __init__(self, ProteinTable):
        self.histogram_plot = self.histograms(ProteinTable.df)
        self.biome_plot = self.biome_distribution(ProteinTable.df)
        self.piechart_plot = self.piecharts(ProteinTable.df)

    def biome_distribution(self, df):
        biomes = [
            "root:Engineered",
            "root:Environmental:Aquatic",
            "root:Environmental:Aquatic:Marine",
            "root:Environmental:Aquatic:Freshwater",
            "root:Environmental:Soil",
            "root:Environmental:Soil:Clay",
            "root:Environmental:Soil:Shrubland",
            "root:Host-associated:Plants",
            "root:Host-associated:Human",
            "root:Host-associated:Human:Digestive system",
            "root:Host-associated:Human:non Digestive system",
            "root:Host-associated:Animal",
            "root:other",
        ]
        biome_counts = (
            pd.DataFrame(df["biome"].apply(lambda x: list(x)).to_list(), columns=biomes)
            .astype(int)
            .sum()
        )
        biome_counts.loc["root:Environmental"] = (
            biome_counts.loc["root:Environmental:Aquatic"]
            + biome_counts.loc["root:Environmental:Soil"]
        )
        biome_counts.loc["root:Host-associated:Human"] = (
            biome_counts.loc["root:Host-associated:Human:Digestive system"]
            + biome_counts.loc["root:Host-associated:Human:non Digestive system"]
        )
        biome_counts.loc["root:Host-associated"] = (
            biome_counts.loc["root:Host-associated:Human"]
            + biome_counts.loc["root:Host-associated:Plants"]
            + biome_counts.loc["root:Host-associated:Animal"]
        )
        biome_counts = biome_counts.reset_index()

        biome_counts["label"] = biome_counts["index"].apply(lambda x: x.split(":")[-1])
        biome_counts["parent"] = biome_counts["index"].apply(lambda x: x.split(":")[-2])
        biome_counts.loc[15] = [
            "root",
            biome_counts[biome_counts["parent"] == "root"][0].sum(),
            "root",
            "",
        ]

        fig = go.Figure(
            go.Sunburst(
                labels=biome_counts.label,
                parents=biome_counts.parent,
                values=biome_counts[0],
                branchvalues="total",
            )
        )
        fig.update_layout(autosize=True, title="Biome Distribution")
        return fig

    def piecharts(self, df):
        # Setup for prettier plots
        hole = 0.3
        textinfo = "label+percent"
        pretty_labels = {
            "PL": {
                "00": "full length",
                "11": "fragment",
                "01": "partial right",
                "10": "partial left",
            },
            "UP": {"0": "not in Uniprot", "1": "in Uniprot"},
            "CR": {"0": "Member", "1": "Representative"},
        }

        def _value_dist(column):
            counts = Counter(column)
            return {"labels": list(counts.keys()), "values": list(counts.values())}

        # Prepare for each plot
        fragments_data = _value_dist(df["PL"])
        fragments_data["labels"] = [
            pretty_labels["PL"][i] for i in fragments_data["labels"]
        ]
        fragments = go.Pie(**fragments_data, hole=hole, textinfo=textinfo, visible=True)

        uniprot_data = _value_dist(df["UP"])
        uniprot_data["labels"] = [
            pretty_labels["UP"][i] for i in uniprot_data["labels"]
        ]
        uniprot = go.Pie(**uniprot_data, hole=hole, textinfo=textinfo, visible=False)

        representative_data = _value_dist(df["CR"])
        representative_data["labels"] = [
            pretty_labels["CR"][i] for i in representative_data["labels"]
        ]
        reps = go.Pie(
            **representative_data, hole=hole, textinfo=textinfo, visible=False
        )

        # Create Figure
        fig = go.Figure()
        fig.add_traces([fragments, uniprot, reps])
        fig.update_layout(
            updatemenus=[
                dict(
                    active=0,
                    buttons=list(
                        [
                            dict(
                                label="Completeness",
                                method="update",
                                args=[
                                    {"visible": [True, False, False]},
                                    {"title": "Protein Completeness"},
                                ],
                            ),
                            dict(
                                label="Uniprot",
                                method="update",
                                args=[
                                    {"visible": [False, True, False]},
                                    {"title": "Uniprot"},
                                ],
                            ),
                            dict(
                                label="Cluster",
                                method="update",
                                args=[
                                    {"visible": [False, False, True]},
                                    {"title": "Clustering"},
                                ],
                            ),
                        ]
                    ),
                )
            ]
        )
        fig.update_layout(autosize=True, title="Completeness")
        return fig

    def histograms(self, df):
        # Setup for prettier plots
        percentage_bins = {"end": 100, "start": 0, "size": 1}

        # Prepare for each plot
        similarity = go.Histogram(
            x=df["similarity"], name="Similarity", visible=True, xbins=percentage_bins
        )
        identity = go.Histogram(
            x=df["identity"], name="Identity", visible=False, xbins=percentage_bins
        )
        q_coverage = go.Histogram(
            x=df["coverage_query"],
            name="Query coverage",
            visible=False,
            xbins=percentage_bins,
        )
        t_coverage = go.Histogram(
            x=df["coverage_hit"],
            name="Target coverage",
            visible=False,
            xbins=percentage_bins,
        )
        tlen = go.Histogram(x=df["tlen"], name="Target length", visible=False)

        # Create Figure
        fig = go.Figure()
        fig.add_traces([similarity, identity, q_coverage, t_coverage, tlen])
        fig.update_layout(
            updatemenus=[
                dict(
                    active=0,
                    buttons=list(
                        [
                            dict(
                                label="Similarity",
                                method="update",
                                args=[
                                    {"visible": [True, False, False, False, False]},
                                    {
                                        "title": "Similarity Distribution",
                                        "xaxis": {"title": "% Similarity"},
                                    },
                                ],
                            ),
                            dict(
                                label="Identity",
                                method="update",
                                args=[
                                    {"visible": [False, True, False, False, False]},
                                    {
                                        "title": "Identity Distribution",
                                        "xaxis": {"title": "% Identity"},
                                    },
                                ],
                            ),
                            dict(
                                label="Query Coverage",
                                method="update",
                                args=[
                                    {"visible": [False, False, True, False, False]},
                                    {
                                        "title": "Query Coverage Distribution",
                                        "xaxis": {"title": "% Query Coverage"},
                                    },
                                ],
                            ),
                            dict(
                                label="Target Coverage",
                                method="update",
                                args=[
                                    {"visible": [False, False, False, True, False]},
                                    {
                                        "title": "Target Coverage Distribution",
                                        "xaxis": {"title": "% Target Coverage"},
                                    },
                                ],
                            ),
                            dict(
                                label="Length",
                                method="update",
                                args=[
                                    {"visible": [False, False, False, False, True]},
                                    {
                                        "title": "Target Length Distribution",
                                        "xaxis": {"title": "length (AA)"},
                                    },
                                ],
                            ),
                        ]
                    ),
                )
            ]
        )
        fig.update_layout(
            autosize=True,
            title="Similarity Distribution",
            yaxis=dict(title_text="n proteins"),
            xaxis=dict(title_text="% Similarity"),
        )
        return fig

    def save(self, output_file: Union[str, Path]):
        with open(output_file, "w") as dashboard:
            dashboard.write("<html><head></head><body>" + "\n")
            for fig in [self.histogram_plot, self.piechart_plot, self.biome_plot]:
                inner_html = fig.to_html().split("<body>")[1].split("</body>")[0]
                dashboard.write(inner_html)
            dashboard.write("</body></html>" + "\n")
