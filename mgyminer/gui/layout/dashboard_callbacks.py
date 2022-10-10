import plotly.express as px
from dash import Input, Output
from gui.index import app

from mgyminer.proteinTable import proteinTable


@app.callback(
    Output("stats-scatter", "figure"),
    Input("data-storage", "data"),
    Input("scatter-xaxis", "value"),
    Input("scatter-yaxis", "value"),
)
def update_scatter(data, xaxis_column_name, yaxis_column_name):
    fig = px.scatter(
        data,
        x=xaxis_column_name,
        y=yaxis_column_name,
        hover_name="target_name",
        marginal_x="histogram",
        marginal_y="histogram",
    )
    fig.update_xaxes(title=xaxis_column_name)
    fig.update_yaxes(title=yaxis_column_name)
    fig.update_layout(clickmode="event+select")
    return fig


@app.callback(Output("data-storage", "data"), Input("csv-input-dropdown", "value"))
def update_storage(filepath):
    return proteinTable(filepath).df.to_dict()
