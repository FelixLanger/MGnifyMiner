import dash_bio
import dash_bootstrap_components as dbc
from dash import dcc, html

alignment_plot = html.Div(
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
            value="Settings",
            children=[
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
                                    html.Div(
                                        className="app-controls-block",
                                        children=[
                                            html.Div(
                                                className="app-controls-name",
                                                children="Colorscale",
                                            ),
                                            dcc.RadioItems(
                                                id="alignment-correctgap-radio",
                                                className="alignment-radio",
                                                options=[
                                                    {"label": "Yes", "value": True},
                                                    {"label": "No", "value": False},
                                                ],
                                                value=True,
                                                labelStyle={
                                                    "display": "inline-block",
                                                    "margin-right": "8px",
                                                },
                                            ),
                                            html.Div(
                                                className="app-controls-desc",
                                                children="Lowers conservation "
                                                "of high gap sequences.",
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

alignment = html.Div(
    id="alignment-box",
    children=[dbc.Row([dbc.Col(alignment_controls), dbc.Col(alignment_plot)])],
)
