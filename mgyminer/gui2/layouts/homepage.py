from mgyminer.gui2.components.statsbar import statsbar
from mgyminer.gui2.components.filters import filter_controls
from mgyminer.gui2.components.scatter import scatter
from mgyminer.gui2.components.metadata import metadata
import dash_bootstrap_components as dbc
from dash import html

# the styles for the main content position it to the right of the sidebar and
# add some padding.

page = html.Div(
    id="page-content",
    children=[
        dbc.Row(statsbar),
        dbc.Row(
            [
                dbc.Col(filter_controls),
                dbc.Col(scatter, className="data-container"),
                dbc.Col(metadata, className="data-container"),
            ],
        ),
        dbc.Row(html.Div(["blabla"])),
    ],
)
