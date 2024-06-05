import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, callback_context

from mgyminer.constants import BIOME_MATRIX, BIOMES
from mgyminer.dashboard.utils.data_store import protein_store
from mgyminer.plotting import create_biome_plot


@callback(
    Output("scatter-xaxis-dropdown", "options"),
    Output("scatter-yaxis-dropdown", "options"),
    Input("apply-filter-btn", "n_clicks"),
)
def update_axis_dropdowns(nklicks):
    pt = protein_store.get_dataframe()

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

    return xaxis_options, yaxis_options


@callback(
    Output("results-scatter", "figure"),
    Input("filtered-data-store", "data"),
    Input("scatter-xaxis-dropdown", "value"),
    Input("scatter-yaxis-dropdown", "value"),
)
def update_scatter(filtered_data, xaxis_column_name, yaxis_column_name):
    pt = pd.DataFrame(filtered_data)

    column_mapping = {
        "tlen": "Target Length",
        "e-value": "e-Value",
        "coverage_query": "Query Coverage",
        "coverage_hit": "Hit Coverage",
        "similarity": "Similarity",
        "identity": "Identity",
    }

    if pt.empty:
        fig = px.scatter()
        fig.update_layout(xaxis_title="", yaxis_title="")
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
        fig.update_xaxes(title_text=column_mapping[xaxis_column_name], overwrite=True, row=1, col=1)
        fig.update_yaxes(title_text=column_mapping[yaxis_column_name], overwrite=True, row=1, col=1)

    fig.update_layout(clickmode="event+select")
    return fig


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
    State("completeness-checklist", "value"),
    State("biome-dropdown", "value"),
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
    truncation,
    biomes,
):
    def create_filter(min_value, max_value):
        filter_dict = {}
        if min_value is not None:
            filter_dict["min"] = min_value
        if max_value is not None:
            filter_dict["max"] = max_value
        return filter_dict if filter_dict else None

    if not callback_context.triggered:
        button_id = None
    else:
        button_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    if button_id == "reset-filter-btn" or button_id is None:
        pt = protein_store.get_dataframe()
        return pt.to_dict("records")
    else:
        pt = protein_store.get_dataframe()
        filter_mapping = {
            "e-value": (e_value_min, e_value_max),
            "identity": (identity_min, identity_max),
            "similarity": (similarity_min, similarity_max),
            "coverage_query": (query_coverage_min, query_coverage_max),
            "coverage_hit": (target_coverage_min, target_coverage_max),
        }

        filters = {
            key: create_filter(min_val, max_val)
            for key, (min_val, max_val) in filter_mapping.items()
            if create_filter(min_val, max_val) is not None
        }
        if 1 <= len(truncation) <= 3:
            # don't filter when all proteins are selected or none are selected
            # all proteins are then returned
            filters["truncation"] = truncation
        if biomes:
            filters["biomes"] = biomes

        filtered_pt = pt.pick(filters)
        return filtered_pt.to_dict("records")


@callback(
    Output("e-value-min", "value"),
    Output("e-value-max", "value"),
    Output("identity-min", "value"),
    Output("identity-max", "value"),
    Output("similarity-min", "value"),
    Output("similarity-max", "value"),
    Output("query-coverage-min", "value"),
    Output("query-coverage-max", "value"),
    Output("target-coverage-min", "value"),
    Output("target-coverage-max", "value"),
    Output("completeness-checklist", "value"),
    Input("reset-filter-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_input_fields(reset_clicks):
    return None, None, None, None, None, None, None, None, None, None, ["00", "01", "10", "11"]


@callback(
    Output("biome-plot", "figure"),
    Input("filtered-data-store", "data"),
    Input("results-scatter", "selectedData"),
)
def update_biome_graph(filtered_data, selected_data):
    if filtered_data:
        df = pd.DataFrame(filtered_data)

        if selected_data:
            selected_points = selected_data["points"]
            selected_indices = [point["pointIndex"] for point in selected_points]
            df = df.loc[selected_indices]

        fig = create_biome_plot(df, biome_column="biomes")
        return fig
    else:
        return {}


@callback(
    Output("completeness-plot", "figure"),
    Input("filtered-data-store", "data"),
    Input("results-scatter", "selectedData"),
)
def update_completeness_barchart(filtered_data, selected_data):
    if filtered_data is None:
        return {}
    df = pd.DataFrame(filtered_data)
    truncation_series = df["truncation"]

    if selected_data:
        selected_points = selected_data["points"]
        selected_indices = [point["pointIndex"] for point in selected_points]
        truncation_series = truncation_series.iloc[selected_indices]

    flattened_list = pd.Series(truncation_series.sum())
    value_counts = flattened_list.value_counts(dropna=False)

    labels = {
        "00": "Complete",
        "01": "C-terminal-truncated",
        "11": "Fragment",
        "10": "N-terminal truncated",
    }

    fig = go.Figure()

    complete_count = value_counts.get("00", 0)
    fig.add_trace(go.Bar(x=["Complete"], y=[complete_count], name="Complete"))

    fragment_counts = {label: value_counts.get(key, 0) for key, label in labels.items() if key != "00"}
    for label, count in fragment_counts.items():
        fig.add_trace(go.Bar(x=["Fragments"], y=[count], name=label))

    fig.update_layout(
        barmode="stack",
        xaxis_title="Completeness",
        yaxis_title="Count",
        legend_title="Fragment Type",
    )

    return fig


@callback(
    Output("selected-proteins-table", "data"),
    Output("selected-proteins-table", "columns"),
    Input("filtered-data-store", "data"),
    Input("results-scatter", "selectedData"),
)
def update_results_table(filtered_data, selected_proteins):
    if filtered_data is None:
        pt = protein_store.get_dataframe()
    else:
        pt = pd.DataFrame.from_records(filtered_data)

    if selected_proteins:
        selected_points = selected_proteins["points"]
        selected_indices = [point["pointIndex"] for point in selected_points]
        pt = pt.iloc[selected_indices]

    display_columns = [
        col
        for col in pt.columns
        if col
        in [
            "target_name",
            "tlen",
            "e-value",
            "coverage_hit",
            "coverage_query",
            "similarity",
            "identity",
            "pfam_architecture",
        ]
    ]
    df = pt[display_columns]
    df.rename(
        {
            "target_name": "Target",
            "tlen": "Length",
            "coverage_hit": "Target Coverage",
            "coverage_query": "Query Coverage",
            "similarity": "Similarity",
            "identity": "Identity",
            "pfam_architecture": "Pfam Architecture",
        },
        inplace=True,
        axis=1,
    )
    columns = [{"name": col, "id": col} for col in df.columns]
    data = df.to_dict("records")
    return data, columns


@callback(
    Output("biome-dropdown", "options"),
    Input("selected-proteins-table", "page_size"),
)
def update_biome_filter_dropdown(n_clicks):
    protein_data = protein_store.get_dataframe()
    dropdown_biome_ids = BIOME_MATRIX.get_unique_parents(protein_data.unique_nested("biomes"))
    dropdown_biome_strings = [BIOMES[biomeid] for biomeid in dropdown_biome_ids]
    biome_levels = sorted(dropdown_biome_strings, key=len)
    biome_options = [{"label": level, "value": level} for level in biome_levels]

    return biome_options
