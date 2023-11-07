from dash import Input, Output
from mgyminer.gui2.app import app
import plotly.express as px
from mgyminer.gui2.utils.data_singleton import DataSingleton


@app.callback(
    Output("stats-scatter", "figure"),
    # Input("data-storage", "data"),
    Input("scatter-xaxis", "value"),
    Input("scatter-yaxis", "value"),
)
def update_scatter(
    # data,
    xaxis_column_name,
    yaxis_column_name,
):
    data = DataSingleton().data.df.to_dict()
    if not data:
        return px.scatter()
    if xaxis_column_name == "e-value":
        log_x = True
    else:
        log_x = False

    if yaxis_column_name == "e-value":
        log_y = True
    else:
        log_y = False
    fig = px.scatter(
        data,
        x=xaxis_column_name,
        y=yaxis_column_name,
        hover_name="target_name",
        marginal_x="histogram",
        marginal_y="histogram",
        log_x=log_x,
        log_y=log_y,
    )
    # fig.update_xaxes(title=xaxis_column_name)
    # fig.update_yaxes(title=yaxis_column_name)
    fig.update_layout(clickmode="event+select")
    return fig
