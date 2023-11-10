import pandas as pd
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from mgyminer.gui2.server import app
from mgyminer.phyltree import treebuilder
from mgyminer.gui2.utils.data_singleton import DataSingleton
from mgyminer.gui2.server import long_callback_manager
from mgyminer.phylplot import plot_tree


@app.long_callback(
    output=Output("tree", "figure"),
    inputs=[
        Input("build-tree-button", "n_clicks"),
    ],
    state=[
        State("filtered-data", "data"),
        State("selected-indices", "data"),
    ],
    running=[
        (Output("build-tree-button", "disabled"), True, False),
        (Output("cancel-tree-button", "disabled"), False, True),
        (
            Output("tree-field", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            Output("progress_bar", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    cancel=[Input("cancel-tree-button", "n_clicks")],
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
    prevent_initial_call=True,
    manager=long_callback_manager,
)
def build_tree(set_progress, n_clicks, data_json, selected_indices):
    total_steps = 6
    progress_step = 0
    set_progress((str(progress_step), str(total_steps)))
    if not data_json:
        raise PreventUpdate
    data = pd.read_json(data_json)
    if selected_indices:
        data = data.iloc[selected_indices]

    progress_step += 1
    set_progress((str(progress_step), str(total_steps)))

    query = DataSingleton().query_file
    hit_sequences = DataSingleton().hit_sequences
    progress_step += 1
    set_progress((str(progress_step), str(total_steps)))

    # Build the tree
    tree = treebuilder(data, query, hit_sequences, "tree.out", "aligmnent.out")
    progress_step += 1
    set_progress((str(progress_step), str(total_steps)))

    # Perform alignment and tree building
    tree.make_alignment()
    progress_step += 1
    set_progress((str(progress_step), str(total_steps)))
    tree.build_tree()
    progress_step += 1
    set_progress((str(progress_step), str(total_steps)))

    # Plot the tree and return the figure
    figure = plot_tree(data, "tree.out")
    progress_step += 1
    set_progress((str(progress_step), str(total_steps)))

    return figure
