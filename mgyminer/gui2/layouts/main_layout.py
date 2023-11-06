from dash import html, dcc
from mgyminer.gui2.components import sidebar
from mgyminer.gui2.layouts import homepage

layout = html.Div([dcc.Location(id="url"), sidebar.sidebar, homepage.page])
