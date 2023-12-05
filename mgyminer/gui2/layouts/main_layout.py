from dash import html, dcc
from mgyminer.gui2.components import sidebar
from mgyminer.gui2.layouts import homepage

layout = html.Div(
    [
        dcc.Location(id="url"),
        dcc.Store(id="filter-parameters", storage_type="session"),
        dcc.Store(id="filtered-data", storage_type="session"),
        dcc.Store(id="selected-indices", storage_type="session"),
        # sidebar.sidebar,
        homepage.page,
    ]
)
