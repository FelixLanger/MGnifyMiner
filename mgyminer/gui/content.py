from dash import html
from gui.index import app
from gui.layout.dashboard import controls, plots
from gui.layout.dashboard_callbacks import update_scatter, update_storage  # noqa: F401
from gui.layout.header import header

app.layout = html.Div(
    [header, html.Div(id="body", className="app-body", children=[controls, plots])]
)
