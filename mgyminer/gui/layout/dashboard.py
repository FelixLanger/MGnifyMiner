from pathlib import Path

import dash_bootstrap_components as dbc
from dash import dcc, html


def figure(plot):
    return html.Div(
        [
            dbc.Card(dbc.CardBody([dcc.Graph(id=plot)])),
        ]
    )


def dropdown_cwd_options():
    cwd = Path.cwd()
    files = sorted(f for f in Path(cwd).iterdir() if f.is_file())
    return [{"label": file.name, "value": str(file)} for file in files]


controls = html.Div(
    id="app-control-tabs",
    className="control-tabs",
    children=[
        dcc.Tabs(
            id="dashboard-tabs",
            value="data",
            children=[
                dcc.Tab(
                    label="Data",
                    value="data",
                    children=html.Div(
                        className="control-tab",
                        children=[
                            html.H4(
                                children="Setup Input Files",
                            ),
                            html.Div(
                                className="app-controls-block",
                                children=[
                                    html.Div(
                                        className="fullwidth-app-controls-name",
                                        children="Select results csv",
                                    ),
                                    dcc.Dropdown(
                                        id="csv-input-dropdown",
                                        options=dropdown_cwd_options(),
                                    ),
                                ],
                            ),
                            html.Div(
                                className="app-controls-block",
                                children=[
                                    html.Div(
                                        className="fullwidth-app-controls-name",
                                        children="Select treefile",
                                    ),
                                    dcc.Dropdown(
                                        id="tree-input-dropdown",
                                        options=dropdown_cwd_options(),
                                    ),
                                ],
                            ),
                            html.Div(
                                className="app-controls-block",
                                children=[
                                    html.Div(
                                        className="fullwidth-app-controls-name",
                                        children="Select query fasta",
                                    ),
                                    dcc.Dropdown(
                                        id="queryfasta-input-dropdown",
                                        options=dropdown_cwd_options(),
                                    ),
                                ],
                            ),
                            html.Div(
                                className="app-controls-block",
                                children=[
                                    html.Div(
                                        className="fullwidth-app-controls-name",
                                        children="Select all sequences fasta",
                                    ),
                                    dcc.Dropdown(
                                        id="sequences-input-dropdown",
                                        options=dropdown_cwd_options(),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                dcc.Tab(
                    label="Filters",
                    value="filters",
                    children=html.Div(
                        className="control-tab",
                        children=[
                            html.H4(
                                children="Filter Data",
                            ),
                            html.Div(
                                className="app-controls-block",
                                children=[
                                    html.Div(
                                        className="fullwidth-app-controls-name",
                                        children="E-Value Filter",
                                    ),
                                    dcc.Input(
                                        id="e-value-min",
                                        type="number",
                                        placeholder="Min",
                                        min=0,
                                        max=100,
                                        step=1,
                                    ),
                                    dcc.Input(
                                        id="e-value-max",
                                        type="number",
                                        placeholder="Max",
                                        min=0,
                                        max=100,
                                        step=1,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="app-controls-block",
                                children=[
                                    html.Div(
                                        className="fullwidth-app-controls-name",
                                        children="Identity Filter",
                                    ),
                                    dcc.Input(
                                        id="identity-min",
                                        type="number",
                                        placeholder="Min",
                                        min=0,
                                        max=100,
                                        step=1,
                                    ),
                                    dcc.Input(
                                        id="identity-max",
                                        type="number",
                                        placeholder="Max",
                                        min=0,
                                        max=100,
                                        step=1,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="app-controls-block",
                                children=[
                                    html.Div(
                                        className="fullwidth-app-controls-name",
                                        children="Similarity Filter",
                                    ),
                                    dcc.Input(
                                        id="similarity-min",
                                        type="number",
                                        placeholder="Min",
                                        min=0,
                                        max=100,
                                        step=1,
                                    ),
                                    dcc.Input(
                                        id="similarity-max",
                                        type="number",
                                        placeholder="Max",
                                        min=0,
                                        max=100,
                                        step=1,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        )
    ],
)

plot_axes = [
    {"label": "Target Length", "value": "tlen"},
    {"label": "E-Value", "value": "e-value"},
    {"label": "Hit Coverage", "value": "coverage_hit"},
    {"label": "Query Coverage", "value": "coverage_query"},
    {"label": "Similarity", "value": "similarity"},
    {"label": "Identity", "value": "identity"},
]

scatter = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Label("X-Axis:", htmlFor="scatter-xaxis"),
                                dcc.Dropdown(
                                    options=plot_axes,
                                    value="e-value",
                                    id="scatter-xaxis",
                                ),
                            ]
                        )
                    ),
                    dbc.Col(
                        [
                            html.Label("Y-Axis:"),
                            dcc.Dropdown(
                                options=plot_axes,
                                value="similarity",
                                id="scatter-yaxis",
                            ),
                        ]
                    ),
                ]
            ),
            dbc.Row(dcc.Graph(id="stats-scatter")),
        ]
    )
)

metadata = dbc.Card(
    dbc.CardBody(
        dbc.Tabs(
            [
                dbc.Tab(dcc.Graph(id="completeness"), label="Completeness"),
                dbc.Tab(dcc.Graph(id="biome"), label="Biome"),
            ]
        )
    )
)

plots = html.Div(
    id="dashboard-plots",
    children=[dbc.CardGroup([scatter, metadata, dcc.Store(id="data-storage")])],
)
filtercard = html.Div(dbc.Card(dbc.CardBody(dbc.Row())))
