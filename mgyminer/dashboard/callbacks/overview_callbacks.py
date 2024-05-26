from dash import Input, Output, State, callback, callback_context
from mgyminer.dashboard.utils.data_store import protein_store
import plotly.express as px
import pandas as pd


@callback(
    Output("results-scatter", "figure"),
    Output("scatter-xaxis-dropdown", "options"),
    Output("scatter-xaxis-dropdown", "value"),
    Output("scatter-yaxis-dropdown", "options"),
    Output("scatter-yaxis-dropdown", "value"),
    Input("filtered-data-store", "data"),
    Input("scatter-xaxis-dropdown", "value"),
    Input("scatter-yaxis-dropdown", "value"),
    State("scatter-xaxis-dropdown", "options"),
    State("scatter-yaxis-dropdown", "options"),
)
def update_scatter(
    filtered_data,
    xaxis_column_name,
    yaxis_column_name,
    current_xaxis_options,
    current_yaxis_options,
):
    pt = pd.DataFrame(filtered_data)

    column_mapping = {
        "tlen": "Target Length",
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
    fig.update_xaxes(title_text=column_mapping[xaxis_column_name], overwrite=True, row=1, col=1)
    fig.update_yaxes(title_text=column_mapping[yaxis_column_name], overwrite=True, row=1, col=1)
    return fig, xaxis_options, xaxis_column_name, yaxis_options, yaxis_column_name


@callback(
    Output("filtered-data-store", "data"),
    Input("apply-filter-btn", "n_clicks"),
    Input("reset-filter-btn", "n_clicks"),
    State("e-value-min", "value"),
    State("e-value-max", "value"),
    State("identity-min", "value"),
    State("identity-max", "value"),
    State("similarity-min", "value"),
    State("similarity-max", "value"),
    State("query-coverage-min", "value"),
    State("query-coverage-max", "value"),
    State("target-coverage-min", "value"),
    State("target-coverage-max", "value"),
)
def update_filtered_data(
    apply_clicks,
    reset_clicks,
    e_value_min,
    e_value_max,
    identity_min,
    identity_max,
    similarity_min,
    similarity_max,
    query_coverage_min,
    query_coverage_max,
    target_coverage_min,
    target_coverage_max,
):
    if not callback_context.triggered:
        button_id = None
    else:
        button_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    if button_id == "reset-filter-btn" or button_id is None:
        pt = protein_store.get_dataframe()
        return pt.to_dict("records")
    else:
        pt = protein_store.get_dataframe()
        filters = {}

        if e_value_min is not None or e_value_max is not None:
            filters["e-value"] = {"min": e_value_min, "max": e_value_max}
        if identity_min is not None or identity_max is not None:
            filters["identity"] = {"min": identity_min, "max": identity_max}
        if similarity_min is not None or similarity_max is not None:
            filters["similarity"] = {"min": similarity_min, "max": similarity_max}
        if query_coverage_min is not None or query_coverage_max is not None:
            filters["coverage_query"] = {"min": query_coverage_min, "max": query_coverage_max}
        if target_coverage_min is not None or target_coverage_max is not None:
            filters["coverage_hit"] = {"min": target_coverage_min, "max": target_coverage_max}

        filtered_pt = pt.pick(filters)
        return filtered_pt.to_dict("records")