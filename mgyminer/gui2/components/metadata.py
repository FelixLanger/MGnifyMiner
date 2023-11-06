import dash_bootstrap_components as dbc
from dash import dcc


metadata = dbc.Card(className="data-card", children=
    dbc.CardBody(children=
        dbc.Tabs(
            [
                dbc.Tab(dcc.Graph(id="completeness"), label="Completeness"),
                dbc.Tab(dcc.Graph(id="biome"), label="Biome"),
            ]
        )
    )
)