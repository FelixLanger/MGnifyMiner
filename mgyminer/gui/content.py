from dash import html
from gui.index import app
from gui.layout.dashboard import (
    alignment,
    alignment_controls,
    controls,
    plots,
    treesection,
)
from gui.layout.dashboard_callbacks import (  # noqa: F401
    alignment_callbacks,
    load_storage,
    update_scatter,
)
from gui.layout.header import header

app.layout = html.Div(
    [
        header,
        html.Div(
            id="overview-module", className="app-body", children=[controls, plots]
        ),
        html.Div(id="tree-moduke", className="app-body", children=[treesection]),
        html.Div(
            id="alignment-module",
            className="app-body",
            children=[alignment_controls, alignment],
        ),
    ]
)

alignment_callbacks(app)
