import dash_bootstrap_components as dbc
from dash import html
from mgyminer.gui2.utils.data_singleton import DataSingleton

total_hits = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Total hits:", className="card-title"),
            html.P(f"{len(DataSingleton().data.df)}",
                id="hit-count",
                className="card-text",
            ),
        ]
    ),
    style={"width": "18rem"},
)

total_pfam_architectures = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Pfam Architectures:", className="card-title"),
            html.P(f"{DataSingleton().data.df['pfam_architecture'].nunique()}",
                id="pfam-count",
                className="card-text",
            ),
        ]
    ),
    style={"width": "18rem"},
)

total_biomes = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Biomes:", className="card-title"),
            html.P(f"{len(DataSingleton().data._nunique_nested('biomes'))}",
                id="biome-count",
                className="card-text",
            ),
        ]
    ),
    style={"width": "18rem"},
)

## TODO Count from how many clusters the hits are

statsbar = html.Div(
    id="statsbar",
    className="statsbar",
    children=[
        dbc.Row([
                dbc.Col(html.Div(total_hits)),
                dbc.Col(html.Div(total_pfam_architectures)),
                dbc.Col(html.Div(total_biomes)),
        ])
    ]
)

