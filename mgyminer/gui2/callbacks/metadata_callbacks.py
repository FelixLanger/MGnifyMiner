import json

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, exceptions

from mgyminer.constants import BIOMES
from mgyminer.gui2.app import app


@app.callback(
    Output("completeness-plot", "figure"),
    [
        Input("filtered-data", "data"),
        Input("selected-indices", "data"),
    ],
)
def update_completeness_barchart(data_json, selected_indices):
    if not data_json:
        raise exceptions.PreventUpdate
    truncation_data = json.loads(data_json).get("truncation")
    truncation_series = pd.Series(truncation_data)
    if selected_indices:
        truncation_series = truncation_series[truncation_series.index.isin([str(i) for i in selected_indices])]
    flattened_list = pd.Series([item for sublist in truncation_series for item in sublist])
    value_counts = flattened_list.value_counts(dropna=False)
    print(value_counts)
    labels = {
        0: "complete",
        1: "C-terminal-truncated",
        11: "fragment",
        10: "N-terminal truncated",
        pd.NA: "no info",
    }

    # Initialize the figure
    fig = go.Figure()

    # Handle 'complete' category separately to place it in its own bar
    complete_count = value_counts.get(0, 0)
    fig.add_trace(go.Bar(x=["complete"], y=[complete_count], name="Complete"))

    # Initialize fragments total count
    fragments_total = 0

    # Add traces for other categories dynamically
    for value, label in labels.items():
        if pd.isna(value):
            # Handle the NaN/NA case
            count = value_counts.get(pd.NA, 0)
        else:
            if value == 0:  # Skip 'complete' as it's already added
                continue
            count = value_counts.get(value, 0)  # Get the count or default to 0

        fragments_total += count  # Add to the fragments total
        fig.add_trace(go.Bar(x=["fragments"], y=[count], name=label))

    # Update the fragments bar to have the total count
    # This assumes that the "complete" bar is the first trace
    fig.data[0].y = [complete_count, fragments_total]

    # Set the bar mode to stack
    fig.update_layout(barmode="stack")

    return fig


@app.callback(
    Output("biome-plot", "figure"),
    [
        Input("filtered-data", "data"),
        Input("selected-indices", "data"),
    ],
)
def update_biome_sunburst_plot(data_json, selected_indices):
    if not data_json:
        raise exceptions.PreventUpdate
    biome_data = json.loads(data_json).get("biomes")

    if selected_indices:
        str_indices = [str(i) for i in selected_indices]
        biome_data = {key: biome_data[key] for key in biome_data if key in str_indices}

    flattened_values = [BIOMES[biomeid] for index, biomelist in biome_data.items() for biomeid in biomelist]

    df = build_sunburst_dataframe(flattened_values)
    fig = go.Figure(
        go.Sunburst(
            ids=df["id"],
            labels=df["label"],
            parents=df["parent"],
            values=df["value"],
            branchvalues="total",  # 'total' or 'remainder'
        )
    )

    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        # uniformtext=dict(minsize=10, mode='hide'), # hides too small text but cancels transitions
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


def build_sunburst_dataframe(biome_list, root_label="root"):
    # Initialize a dictionary to hold counts for each level
    levels_count = {}

    # Process each item in the biome list
    for biome in biome_list:
        parts = biome.split(":")
        for depth in range(1, len(parts) + 1):
            # Create an ID for the current level
            level_id = ":".join(parts[:depth])
            # Increment the count for this level ID
            levels_count[level_id] = levels_count.get(level_id, 0) + 1

    # Build the DataFrame rows
    data_rows = []
    for level_id, count in levels_count.items():
        parts = level_id.split(":")
        # The 'id' is the level_id itself
        row_id = level_id
        # The 'parent' is one level up, except for the root level
        # If there is no parent (at the root level), use the specified root_label
        row_parent = ":".join(parts[:-1]) if len(parts) > 1 else root_label
        # The 'value' is the count for this level
        row_value = count
        # Optionally, 'label' can be the last part of the level_id
        row_label = parts[-1]

        # Ensure the root label itself has no parent
        if row_parent == row_id:  # This happens when we are at the root level
            row_parent = ""

        data_rows.append({"id": row_id, "parent": row_parent, "value": row_value, "label": row_label})

    # Create the DataFrame
    df = pd.DataFrame(data_rows, columns=["id", "parent", "value", "label"])

    # Adjust root entries
    for i, row in df.iterrows():
        if row["id"] == root_label and row["parent"] == "":
            df.at[i, "parent"] = None

    return df
