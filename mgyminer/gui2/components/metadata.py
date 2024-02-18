import dash_bootstrap_components as dbc
from dash import dcc

metadata = dbc.Card(
    className="data-card",
    children=dbc.CardBody(
        children=dbc.Tabs(
            [
                dbc.Tab(dcc.Graph(id="completeness-plot"), label="Completeness"),
                dbc.Tab(dcc.Graph(id="biome-plot"), label="Biome"),
            ]
        )
    ),
)
