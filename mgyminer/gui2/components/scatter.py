from dash import html, dcc
import dash_bootstrap_components as dbc

plot_axes = [
    {"label": "Target Length", "value": "tlen"},
    {"label": "E-Value", "value": "e-value"},
    {"label": "Hit Coverage", "value": "coverage_hit"},
    {"label": "Query Coverage", "value": "coverage_query"},
    {"label": "Similarity", "value": "similarity"},
    {"label": "Identity", "value": "identity"},
]

scatter = dbc.Card(className="data-card", children=
    dbc.CardBody(
        [
            html.H4("Protein Hits", className="card-title"),
            dbc.Row(dcc.Graph(id="stats-scatter")),
            html.H6("Pick Axes:"),
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

        ]
    )
)