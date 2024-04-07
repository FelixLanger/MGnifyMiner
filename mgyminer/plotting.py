from collections import defaultdict

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .constants import BIOMES


def create_sunburst_count_table(df, biome_column="biome", root_label="root"):
    """
    Creates a count table with columns "id", "parent", "value", "label" which is needed
    for the plotly sunburst plot used in the biome visualization.

    The function takes a ProteinTable or DataFrame as input, and the column name
    containing the biome information. This column can either have a single biome or multiple biomes inside a list.
    The biomes can be represented as biome IDs or strings.

    If the biome column contains lists, the function flattens the lists and converts biome IDs to biome strings
    using the BIOMES dictionary.

    Args:
        df (pandas.DataFrame): The input dataframe containing biome data.
        biome_column (str, optional): The name of the column containing biome information.
            Defaults to "biome".
        root_label (str, optional): The label for the root node of the sunburst chart.
            Defaults to "root".

    Returns:
        pandas.DataFrame: A dataframe formatted for creating a sunburst chart, with columns
            "id", "parent", "value", and "label".
    """

    # Check if the column is a list of biomes or single biomes
    if isinstance(df[biome_column].iloc[0], list):
        biome_series = pd.Series(np.concatenate(df[biome_column].values))
    else:
        biome_series = df[biome_column]
    # and convert biome ids to biome strings if needed
    if np.issubdtype(type(biome_series.iloc[0]), np.integer):
        biome_series = biome_series.map(BIOMES)

    levels_count = defaultdict(int)

    def count_levels(biome):
        parts = biome.split(":")
        for depth in range(1, len(parts) + 1):
            level_id = ":".join(parts[:depth])
            levels_count[level_id] += 1

    biome_series.apply(count_levels)

    data_rows = [
        {
            "id": level_id,
            "parent": ":".join(level_id.split(":")[:-1]) if ":" in level_id else root_label,
            "value": count,
            "label": level_id.split(":")[-1],
        }
        for level_id, count in levels_count.items()
    ]

    sunburst_df = pd.DataFrame(data_rows, columns=["id", "parent", "value", "label"])
    sunburst_df.loc[sunburst_df["id"] == root_label, "parent"] = ""

    return sunburst_df


def create_biome_plot(df, biome_column="biome"):
    """
    Creates a sunburst plot visualizing the biome distribution from a given dataframe.
    Args:
        df (pandas.DataFrame): The input dataframe containing biome data.
        biome_column (str, optional): The name of the column containing biome information.
            Defaults to "biome".

    Returns:
        plotly.graph_objects.Figure: A plotly figure object representing the biome sunburst plot.
    """
    sunburst_df = create_sunburst_count_table(df, biome_column)
    fig = go.Figure(
        go.Sunburst(
            ids=sunburst_df["id"],
            labels=sunburst_df["label"],
            parents=sunburst_df["parent"],
            values=sunburst_df["value"],
            branchvalues="total",
        )
    )

    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        sunburstcolorway=[
            "#636efa",
            "#ef553b",
            "#00cc96",
            "#ab63fa",
            "#19d3f3",
            "#e763fa",
            "#fecb52",
            "#ffa15a",
            "#ff6692",
            "#b6e880",
        ],
        extendsunburstcolors=True,
    )
    return fig
