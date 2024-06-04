import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

dash.register_page(__name__)

plot_axes = [
    {"label": "Target Length", "value": "tlen"},
    {"label": "E-Value", "value": "e-value"},
    {"label": "Hit Coverage", "value": "coverage_hit"},
    {"label": "Query Coverage", "value": "coverage_query"},
    {"label": "Similarity", "value": "similarity"},
    {"label": "Identity", "value": "identity"},
]

setting_bar = html.Div(
    className="settings-sidebar",
    children=[
        html.H4("Settings", className="mb-4"),
        dbc.Button("Create Tree", id="create-tree-btn", color="primary", className="mb-3"),
        dbc.Switch(
            id="show-domains-switch",
            label="Show Domains",
            value=True,
            className="mb-3",
        ),
    ],
)

analysis_container = dbc.Container(
    fluid=True,
    className="analysis-content",
    children=[
        dbc.Row(
            className="plots-container",
            children=[
                dbc.Col(
                    className="histogram-container",
                    children=[
                        dbc.Container(
                            className="plot-card",
                            children=[dcc.Graph(id="results-scatter", config={"displaylogo": False})],
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        [
                                            html.Label("X-Axis:", htmlFor="scatter-xaxis-dropdown"),
                                            dcc.Dropdown(
                                                options=plot_axes,
                                                value="e-value",
                                                id="scatter-xaxis-dropdown",
                                                clearable=False,
                                            ),
                                        ]
                                    )
                                ),
                                dbc.Col(
                                    [
                                        html.Label("Y-Axis:", htmlFor="scatter-xaxis-dropdown"),
                                        dcc.Dropdown(
                                            options=plot_axes,
                                            value="similarity",
                                            id="scatter-yaxis-dropdown",
                                            clearable=False,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
    ],
)

additional_analysis_container = dbc.Container(
    fluid=True,
    className="analysis-content",
    children=[
        dbc.Row(
            className="plots-container",
            children=[
                dbc.Col(
                    className="histogram-container",
                    children=[
                        dbc.Container(
                            className="plot-card",
                            children=[dcc.Graph(id="additional-scatter", config={"displaylogo": False})],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

layout = html.Div(
    className="analysis-layout",
    children=[
        dbc.Container(
            fluid=True,
            className="analysis-container",
            children=[
                setting_bar,
                analysis_container,
                additional_analysis_container,
            ],
        )
    ],
)
