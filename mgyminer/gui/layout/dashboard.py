from pathlib import Path

import dash_bio
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
                            # TODO Field for treefile output name
                            # html.Div(
                            #     className="app-controls-block",
                            #     children=[
                            #         html.Div(
                            #             className="fullwidth-app-controls-name",
                            #             children="Select treefile",
                            #         ),
                            #         dcc.Dropdown(
                            #             id="tree-input-dropdown",
                            #             options=dropdown_cwd_options(),
                            #         ),
                            #     ],
                            # ),
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
                            dbc.Button("Apply", id="files-button", n_clicks=0),
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
                                        max=10,
                                    ),
                                    dcc.Input(
                                        id="e-value-max",
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
                                    ),
                                    dcc.Input(
                                        id="similarity-max",
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
                                    dbc.Button(
                                        "Submit", id="submit-filter", n_clicks=0
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

treesection = dbc.Row(
    [
        html.H2("Phylogenetic tree"),
        html.Div(
            "Select proteins in scatter plot and press the button to start the pylogenetic tree building"
        ),
        html.Br(),
        html.Div(
            [
                dbc.Button(id="build-tree-button", children="Create phylogenetic tree"),
                dbc.Button(id="cancel-tree-button", children="Cancel tree creation"),
            ]
        ),
        dbc.Progress(id="progress_bar", animated=True, striped=True),
        html.Div([figure("tree")], id="tree-field", style={"visibility": "hidden"}),
    ]
)

plots = html.Div(
    id="dashboard-plots",
    className="data-field",
    children=[dbc.CardGroup([scatter, metadata, dcc.Store(id="data-storage")])],
)

alignment = html.Div(
    id="alignment-field",
    className="data-field",
    style={"visibility": "hidden"},
    children=[
        dcc.Loading(
            className="data-field",
            children=[
                dash_bio.AlignmentChart(
                    id="alignment-chart",
                    data=">NOALIGNMENT\nNOALIGNMENT",
                    showgap=False,
                    showconsensus=False,
                    showid=False,
                )
            ],
        )
    ],
)


alignment_controls = html.Div(
    id="alignment-controls",
    className="control-tabs",
    children=[
        dcc.Tabs(
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
                                        children="Select alignment file",
                                    ),
                                    dcc.Dropdown(
                                        id="alignment-input-dropdown",
                                        options=dropdown_cwd_options(),
                                    ),
                                ],
                            ),
                            dbc.Button("Apply", id="alignment-button", n_clicks=0),
                        ],
                    ),
                ),
                dcc.Tab(
                    label="Settings",
                    value="ali-settings",
                    children=html.Div(
                        className="control-tab",
                        children=[
                            html.Div(
                                [
                                    html.H4(
                                        children="Alignment Settings",
                                    ),
                                    html.Div(
                                        className="app-controls-block",
                                        children=[
                                            html.H3(
                                                "General",
                                                className="alignment-settings-section",
                                            ),
                                            html.Div(
                                                className="app-controls-name",
                                                children="Navigation",
                                            ),
                                            dcc.Dropdown(
                                                id="alignment-overview-dropdown",
                                                className="app-controls-block-dropdown",
                                                options=[
                                                    {
                                                        "label": "Heatmap",
                                                        "value": "heatmap",
                                                    },
                                                    {
                                                        "label": "Slider",
                                                        "value": "slider",
                                                    },
                                                    {"label": "None", "value": "none"},
                                                ],
                                                value="none",
                                            ),
                                            html.Div(
                                                className="app-controls-desc",
                                                children="Show slider, heatmap or no overview for navigation.",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="app-controls-block",
                                        children=[
                                            html.Div(
                                                className="app-controls-name",
                                                children="Consensus",
                                            ),
                                            dcc.RadioItems(
                                                id="alignment-showconsensus-radio",
                                                className="alignment-radio",
                                                options=[
                                                    {"label": "Show", "value": True},
                                                    {"label": "Hide", "value": False},
                                                ],
                                                value=True,
                                                labelStyle={
                                                    "display": "inline-block",
                                                    "margin-right": "8px",
                                                },
                                            ),
                                            html.Div(
                                                className="app-controls-desc",
                                                children="Toggle the consensus "
                                                "(most frequent) sequence.",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="app-controls-block",
                                        children=[
                                            html.Div(
                                                className="app-controls-name",
                                                children="Text size",
                                            ),
                                            dcc.Slider(
                                                className="control-slider",
                                                id="alignment-textsize-slider",
                                                value=10,
                                                min=8,
                                                max=12,
                                                step=1,
                                                marks={
                                                    8: "8",
                                                    9: "9",
                                                    10: "10",
                                                    11: "11",
                                                    12: "12",
                                                },
                                            ),
                                            html.Div(
                                                className="app-controls-desc",
                                                children="Adjust the font size "
                                                "(in px) of viewer text.",
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                            html.Hr(),
                            html.Div(
                                [
                                    html.H3(
                                        "Sideplots",
                                        className="alignment-settings-section",
                                    ),
                                    html.Div(
                                        className="app-controls-block",
                                        children=[
                                            html.Div(
                                                className="app-controls-name",
                                                children="Consercation Barplot",
                                            ),
                                            dcc.RadioItems(
                                                id="alignment-showconservation-radio",
                                                className="alignment-radio",
                                                options=[
                                                    {"label": "Show", "value": True},
                                                    {"label": "Hide", "value": False},
                                                ],
                                                value=True,
                                                labelStyle={
                                                    "display": "inline-block",
                                                    "margin-right": "8px",
                                                },
                                            ),
                                            html.Div(
                                                className="app-controls-desc",
                                                children="Show or hide the conservation barplot.",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="app-controls-block",
                                        children=[
                                            html.Div(
                                                className="app-controls-name",
                                                children="Gap",
                                            ),
                                            dcc.RadioItems(
                                                id="alignment-showgap-radio",
                                                className="alignment-radio",
                                                options=[
                                                    {"label": "Show", "value": True},
                                                    {"label": "Hide", "value": False},
                                                ],
                                                value=True,
                                                labelStyle={
                                                    "display": "inline-block",
                                                    "margin-right": "8px",
                                                },
                                            ),
                                            html.Div(
                                                className="app-controls-desc",
                                                children="Show/hide the gap barplot.",
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                        ],
                    ),
                ),
            ],
        )
    ],
)
