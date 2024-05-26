import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/')

plot_axes = [
    {"label": "Target Length", "value": "tlen"},
    {"label": "E-Value", "value": "e-value"},
    {"label": "Hit Coverage", "value": "coverage_hit"},
    {"label": "Query Coverage", "value": "coverage_query"},
    {"label": "Similarity", "value": "similarity"},
    {"label": "Identity", "value": "identity"},
]

filter_tab = dbc.Tab(
    label="Search",
    children=dbc.Container(
        fluid=True,
        className="control-tab",
        children=[
            html.H4("Search Parameters", className="mb-4"),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H6("E-Value Filter"),
                                dbc.Tooltip(
                                    "The E-value is a measure of the statistical significance of a match.",
                                    target="e-value-tooltip",
                                ),
                            ],
                            id="e-value-tooltip",
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Min",
                            type="number",
                            min=0,
                            max=10,
                            id="e-value-min",
                            className="form-control",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Max",
                            type="number",
                            min=0,
                            id="e-value-max",
                            className="form-control",
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H6("Identity Filter"),
                                dbc.Tooltip(
                                    "Identity is the percentage of identical matches"
                                    " between the query and target sequences.",
                                    target="identity-tooltip",
                                ),
                            ],
                            id="identity-tooltip",
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Min",
                            type="number",
                            min=0,
                            max=100,
                            id="identity-min",
                            className="form-control",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Max",
                            type="number",
                            min=0,
                            max=100,
                            id="identity-max",
                            className="form-control",
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H6("Similarity Filter"),
                                dbc.Tooltip(
                                    "Similarity is the percentage of similar matches "
                                    "between the query and target sequences.",
                                    target="similarity-tooltip",
                                ),
                            ],
                            id="similarity-tooltip",
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Min",
                            type="number",
                            min=0,
                            max=100,
                            id="similarity-min",
                            className="form-control",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Max",
                            type="number",
                            min=0,
                            max=100,
                            id="similarity-max",
                            className="form-control",
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H6("Query Coverage"),
                                dbc.Tooltip(
                                    "Query coverage is the percentage of the query sequence"
                                    " that is covered by the alignment.",
                                    target="query-coverage-tooltip",
                                ),
                            ],
                            id="query-coverage-tooltip",
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Min",
                            type="number",
                            min=0,
                            max=100,
                            id="query-coverage-min",
                            className="form-control",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Max",
                            type="number",
                            min=0,
                            max=100,
                            id="query-coverage-max",
                            className="form-control",
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H6("Hit Coverage"),
                                dbc.Tooltip(
                                    "Hit coverage is the percentage of the target "
                                    "sequence that is covered by the alignment.",
                                    target="hit-coverage-tooltip",
                                ),
                            ],
                            id="hit-coverage-tooltip",
                        ),
                        width=12,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Min",
                            type="number",
                            min=0,
                            max=100,
                            id="target-coverage-min",
                            className="form-control",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Input(
                            placeholder="Max",
                            type="number",
                            min=0,
                            max=100,
                            id="target-coverage-max",
                            className="form-control",
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
        ],
    ),
)

setting_bar = html.Div(
    className="settings-sidebar",
    children=[
        dbc.Tabs(
            children=[
                dbc.Tab(filter_tab, label="Filters"),
            ]
        )
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
                        dbc.Container(className="plot-card", children=[dcc.Graph(id="results-scatter")]),
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
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
                dbc.Col(
                    dbc.Container(className="plot-card", children=[dcc.Graph(id="upset")]),
                ),
            ],
        ),
    ],

)


layout = html.Div(dbc.Container(
    fluid=True,
    className="analysis-container",
    children=[
        setting_bar,
        analysis_container
    ]
))