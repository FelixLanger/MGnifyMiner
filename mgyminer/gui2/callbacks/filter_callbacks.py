from dash import Input, Output, State, exceptions, ALL, Patch, html, dcc
from mgyminer.gui2.app import app
from mgyminer.gui2.utils.data_singleton import DataSingleton
from mgyminer.constants import BIOMES
from mgyminer.utils import flatten_list


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
        Input({"type": "city-filter-dropdown", "index": ALL}, "value"),
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
    biomes,
):
    if biomes:
        biomes = [biome_descendant[biome] for biome in biomes]
    filter_dict = {
        "completeness": completeness,
        "e_value": {"min": evalmin, "max": evalmax},
        "identity": {"min": identmin, "max": identmax},
        "similarity": {"min": simmin, "max": simmax},
        "biomes": biomes,
    }
    print(filter_dict)
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


@app.callback(
    Output("biome-dropdown-container-div", "children"),
    Input("add-filter-btn", "n_clicks"),
)
def display_dropdowns(n_clicks):
    patched_children = Patch()
    new_dropdown = dcc.Dropdown(
        all_possible_biomes(),
        id={"type": "city-filter-dropdown", "index": n_clicks},
    )
    patched_children.append(new_dropdown)
    return patched_children


@app.callback(
    Output("biome-dropdown-container-output-div", "children"),
    Input({"type": "city-filter-dropdown", "index": ALL}, "value"),
)
def display_output(values):
    return html.Div(
        [html.Div(f"Dropdown {i + 1} = {value}") for (i, value) in enumerate(values)]
    )


def x_level_biomes(biomes, x):
    """
    Return a list of all the biomes with a depth of x or smaller.
    Depth is the level of detail of th biome description
    """

    def get_depth(biome_description):
        return biome_description.count(":")

    return [desc for desc in biomes.values() if get_depth(desc) <= x]


def all_possible_biomes():
    biome_ids = set(flatten_list(DataSingleton().data.df["biomes"].to_list()))
    return sorted([BIOMES[id] for id in biome_ids])


def biome_descendants(biome_dict):
    """
    Returns a mapping of the biome strings : to all biome IDs which are children of this string
    Example:
        'root:Host-associated:Reptile:Oral cavity:Venom gland' : {486, 487}
    """
    descendant_mapping = {biome: set() for biome in biome_dict.values()}
    for biome_id, biome_str in biome_dict.items():
        for key in descendant_mapping:
            if biome_str.startswith(key):
                descendant_mapping[key].add(biome_id)
    return descendant_mapping


biome_descendant = biome_descendants(BIOMES)
