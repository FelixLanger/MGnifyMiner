import dash_bootstrap_components as dbc
from dash import dcc, html

phylogeny = html.Div(
    [
        html.Div(dcc.Graph(id="tree"), id="tree-field", style={"visibility": "hidden"}),
        dbc.Button("Build Tree", id="build-tree-button"),
        dbc.Button("Cancel", id="cancel-tree-button"),
        dcc.Loading(id="loading", children=[html.Div(id="loading-output")]),
        dbc.Progress(id="progress_bar"),
    ],
    id="plot-container",
)
