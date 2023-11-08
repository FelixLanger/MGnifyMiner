from dash import Input, Output, State, exceptions
from mgyminer.gui2.app import app
from mgyminer.gui2.utils.data_singleton import DataSingleton


@app.callback(
    Output("filter-parameters", "data"),
    [
        Input("completeness-checklist", "value"),
        Input("e-value-min", "value"),
        Input("e-value-max", "value"),
        Input("identity-min", "value"),
        Input("identity-max", "value"),
        Input("similarity-min", "value"),
        Input("similarity-max", "value"),
    ],
)
def update_filters_store(
    completeness,
    evalmin,
    evalmax,
    identmin,
    identmax,
    simmin,
    simmax,
):
    filter_dict = {
        "completeness": completeness,
        "e_value": {"min": evalmin, "max": evalmax},
        "identity": {"min": identmin, "max": identmax},
        "similarity": {"min": simmin, "max": simmax},
    }
    return filter_dict


@app.callback(
    Output("filtered-data", "data"),
    [
        Input("apply-filter-button", "n_clicks"),
    ],
    [State("filter-parameters", "data")],
)
def filter_data(n_clicks, filters):
    if n_clicks is None:
        raise exceptions.PreventUpdate

    filtered_df = DataSingleton().data.df

    # Filter for completeness first
    completeness = filters["completeness"]
    if completeness == [0, 10, 1, 11]:
        pass
    elif completeness == [10, 1, 11]:
        filtered_df = filtered_df.query("complete == False")
    elif completeness == [0]:
        filtered_df = filtered_df.query("complete == True")
    else:
        filtered_df = filtered_df.query("truncation in @completeness")

    for key, value in filters.items():
        if key != "completeness":  # Already handled
            min_value = value.get("min")
            max_value = value.get("max")
            # Only apply filters if at least one of min or max is not None
            if min_value is not None or max_value is not None:
                # Construct the query string based on the provided min and max values
                query_parts = []
                if min_value is not None:
                    query_parts.append(f"{key} >= @min_value")
                if max_value is not None:
                    query_parts.append(f"{key} <= @max_value")
                query_str = " and ".join(query_parts)
                filtered_df = filtered_df.query(query_str)

    return filtered_df.to_json()


@app.callback(
    Output("selected-indices", "data"), Input("stats-scatter", "selectedData")
)
def parse_selected_indices(selected_points):
    if not selected_points:
        return []
    return [point["pointIndex"] for point in selected_points["points"]]
