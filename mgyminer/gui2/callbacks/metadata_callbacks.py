from dash import Input, Output
from mgyminer.gui2.app import app
import plotly.express as px
from mgyminer.gui2.utils.data_singleton import DataSingleton
import pandas as pd

@app.callback(
    Output("completeness", "figure"),
    # Input("data-storage", "data"),
    Input("scatter-xaxis", "value"),
    Input("scatter-yaxis", "value"),
)
def update_completeness_barchart(
        x, y
):
    value_counts = DataSingleton().data.df["truncation"].value_counts(dropna=False)

    labels = {
        0: "complete",
        1: "C-terminal-truncated",
        11: "fragment",
        10: "N-terminal truncated",
        pd.NA: "unknown"
    }

    complete_count = value_counts.get("complete", 0)
    fragments_count = value_counts.drop("complete", errors="ignore").sum()

    stacked_df = pd.DataFrame({
        "complete": [complete_count, 0],
        "fragments": [0, fragments_count]
    }, index=["complete", "fragments"])

    return px.bar(stacked_df, x=stacked_df.index, y=["complete"], title="Occurrences of Different Strings in DataFrame Column")