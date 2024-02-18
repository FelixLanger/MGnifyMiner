import dash_bootstrap_components as dbc
from dash import dcc, html

filter_controls = html.Div(
    id="app-control-tabs",
    className="control-tabs",
    children=[
        dcc.Tabs(
            id="filter-tabs",
            children=[
                dcc.Tab(
                    label="Search",
                    children=html.Div(
                        className="control-tab",
                        children=[
                            html.H4(
                                children="Search Parameters",
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
                                        max=10,
                                    ),
                                    dcc.Input(
                                        id="e-value-max",
                                        type="number",
                                        placeholder="Max",
                                        min=0,
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
                                    ),
                                    dcc.Input(
                                        id="identity-max",
                                        type="number",
                                        placeholder="Max",
                                        min=0,
                                        max=100,
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
                                        value=0,
                                    ),
                                    dcc.Input(
                                        id="similarity-max",
                                        type="number",
                                        placeholder="Max",
                                        min=0,
                                        max=100,
                                        value=100,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                dcc.Tab(label="Domains"),
                dcc.Tab(
                    label="Export",
                    children=html.Div(
                        className="control-tab",
                        children=[
                            html.H4(
                                children="Export Results",
                            ),
                            html.Div(
                                className="app-controls-block",
                                children=[
                                    # html.Div(
                                    #     className="fullwidth-app-controls-name",
                                    #     children="Output file path",
                                    # ),    Output("filtered-data", "data"),
                                    dbc.Input(
                                        id="output-file-name-form",
                                        placeholder="output file name",
                                        type="text",
                                    ),
                                    dbc.Button("Export results", id="export-results-button"),
                                    dbc.Alert(
                                        id="export-alert",
                                        is_open=False,
                                        duration=2000,
                                        color="success",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                dcc.Tab(
                    label="Completeness",
                    children=[
                        html.H4(children="Completeness"),
                        html.Div(
                            [
                                dbc.Label("Choose a bunch"),
                                dbc.Checklist(
                                    options=[
                                        {"label": "Full length / complete", "value": 0},
                                        {"label": "N-terminal truncated ", "value": 10},
                                        {"label": "C-terminal truncated", "value": 1},
                                        {"label": "fragments", "value": 11},
                                    ],
                                    value=[0, 10, 1, 11],
                                    id="completeness-checklist",
                                ),
                            ]
                        ),
                    ],
                ),
                # dcc.Tab(
                #     label="Biome",
                #     children=[
                #         html.H4(children="Biomes"),
                #         html.Div(
                #             [
                #                 dbc.Label("Select Biomes"),
                #                 dbc.Button(
                #                     "Add Filter", id="add-filter-btn", n_clicks=0
                #                 ),
                #                 html.Div(
                #                     id="biome-dropdown-container-div", children=[]
                #                 ),
                #                 html.Div(id="biome-dropdown-container-output-div"),
                #             ]
                #         ),
                #     ],
                # ),
            ],
        ),
        html.Div(
            className="submit-button",
            children=[
                dbc.Button("Apply filter", id="apply-filter-button", n_clicks=0),
            ],
        ),
    ],
)
