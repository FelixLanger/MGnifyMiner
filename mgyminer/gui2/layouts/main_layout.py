from dash import dcc, html

from mgyminer.gui2.layouts import homepage

layout = html.Div(
    [
        dcc.Store(id="filter-parameters", storage_type="memory"),
        dcc.Store(id="filtered-data", storage_type="memory"),
        dcc.Store(id="selected-indices", storage_type="memory"),
        homepage.page,
    ]
)
