from dash import Input, Output, State, callback
from mgyminer.dashboard.utils.data_store import protein_store
import plotly.express as px

@callback(
    Output("results-scatter", "figure"),
    Output("scatter-xaxis-dropdown", "options"),
    Output("scatter-xaxis-dropdown", "value"),
    Output("scatter-yaxis-dropdown", "options"),
    Output("scatter-yaxis-dropdown", "value"),
    Input("scatter-xaxis-dropdown", "value"),
    Input("scatter-yaxis-dropdown", "value"),
    State("scatter-xaxis-dropdown", "options"),
    State("scatter-yaxis-dropdown", "options"),
    prevent_initial_call=True,
)
def update_scatter(
    xaxis_column_name,
    yaxis_column_name,
    current_xaxis_options,
    current_yaxis_options,
):
    pt = protein_store.get_dataframe()

    column_mapping = {
        "tlen": "Hit Length",
        "e-value": "e-Value",
        "coverage_query": "Query Coverage",
        "coverage_hit": "Hit Coverage",
        "similarity": "Similarity",
        "identity": "Identity",
    }

    available_columns = [col for col in column_mapping if col in pt.columns]

    xaxis_options = [{"label": column_mapping[col], "value": col} for col in available_columns]
    yaxis_options = [{"label": column_mapping[col], "value": col} for col in available_columns]

    if not current_xaxis_options:
        xaxis_column_name = available_columns[0] if available_columns else None
    if not current_yaxis_options:
        yaxis_column_name = available_columns[1] if len(available_columns) > 1 else None

    if xaxis_column_name is None or yaxis_column_name is None or pt.empty:
        fig = px.scatter()
    else:
        log_x = xaxis_column_name == "e-value"
        log_y = yaxis_column_name == "e-value"

        fig = px.scatter(
            pt,
            x=xaxis_column_name,
            y=yaxis_column_name,
            hover_name="target_name",
            marginal_x="histogram",
            marginal_y="histogram",
            log_x=log_x,
            log_y=log_y,
        )

    fig.update_layout(clickmode="event+select")
    fig.update_xaxes(title_text="xaxis_label", overwrite=True, row=1, col=1)
    fig.update_yaxes(title_text="yaxis_label", overwrite=True, row=1, col=1)
    return fig, xaxis_options, xaxis_column_name, yaxis_options, yaxis_column_name