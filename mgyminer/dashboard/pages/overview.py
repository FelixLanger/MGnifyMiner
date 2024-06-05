import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

dash.register_page(__name__, path="/")

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

completeness_tab = dbc.Tab(
    label="Completeness",
    children=dbc.Container(
        fluid=True,
        children=[
            html.Div(
                children=[
                    html.H4("Completeness", className="mb-4"),
                    dbc.Checklist(
                        options=[
                            {"label": "Full length / complete", "value": "00"},
                            {"label": "N-terminal truncated", "value": "10"},
                            {"label": "C-terminal truncated", "value": "01"},
                            {"label": "Fragments", "value": "11"},
                        ],
                        value=["00", "10", "01", "11"],
                        id="completeness-checklist",
                        inline=True,
                        className="mb-3",
                    ),
                ]
            ),
            html.Div(
                [
                    html.H6("Biome Filter"),
                    dbc.Tooltip(
                        "Select the biome(s) to filter the data.",
                        target="biome-filter",
                    ),
                ],
                id="biome-filter",
                className="mt-3",
            ),
            dcc.Dropdown(
                id="biome-dropdown",
                options=[],
                value=None,
                multi=True,
                searchable=True,
                clearable=True,
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
                dbc.Tab(completeness_tab, label="Completeness"),
            ]
        ),
        html.Div(
            className="filter-buttons",
            children=[
                dbc.Button("Apply Filter", id="apply-filter-btn", color="primary", className="filter-button"),
                dbc.Button("Reset Filter", id="reset-filter-btn", color="secondary", className="filter-button"),
            ],
        ),
    ],
)


data_table = html.Div(
    className="dtss",
    children=dash_table.DataTable(
        id="selected-proteins-table",
        data=[],
        style_table={"width": "100%", "margin": "0 auto"},
        style_cell={
            "textAlign": "center",
            "padding": "2px",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_header={
            "backgroundColor": "rgb(230, 230, 230)",
            "fontWeight": "bold",
            "textAlign": "center",
            "padding": "2px",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "rgb(248, 248, 248)",
            },
            {
                "if": {"column_id": "column_name"},  # Replace "column_name" with the actual column ID
                "whiteSpace": "normal",
                "width": "auto",  # Set the width to auto to fit the content
            },
        ],
        page_size=10,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        export_format="csv",
        # row_selectable="single",
    ),
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
                dbc.Col(
                    dbc.Container(
                        className="plot-card",
                        children=[
                            dcc.Tabs(
                                id="plot-tabs",
                                value="biome-plot",
                                children=[
                                    dcc.Tab(
                                        label="Biome",
                                        value="biome-plot",
                                        children=[dcc.Graph(id="biome-plot", config={"displaylogo": False})],
                                    ),
                                    dcc.Tab(
                                        label="Completeness",
                                        value="completeness-plot",
                                        children=[dcc.Graph(id="completeness-plot", config={"displaylogo": False})],
                                    ),
                                ],
                            )
                        ],
                    ),
                ),
            ],
        ),
        dbc.Row(className="plots-container", children=data_table),
    ],
)

layout = html.Div(  # dbc.Container(fluid=True,
    className="analysis-container",
    children=[setting_bar, analysis_container],
    #             )
)
