from dash import Input, Output
from dash.exceptions import PreventUpdate

from mgyminer.gui2.server import app


@app.callback(
    Output("alignment-chart", "overview"),
    Input("alignment-overview-dropdown", "value"),
)
def customize_overview(val):
    return val


@app.callback(
    Output("alignment-chart", "showconsensus"),
    [Input("alignment-showconsensus-radio", "value")],
)
def customize_showconsensus(val):
    return val


@app.callback(
    Output("alignment-chart", "showconservation"),
    [Input("alignment-showconservation-radio", "value")],
)
def customize_showconservation(val):
    return val


@app.callback(
    Output("alignment-chart", "showgap"),
    [Input("alignment-showgap-radio", "value")],
)
def customize_showgap(val):
    return val


@app.callback(
    Output("alignment-chart", "textsize"),
    [Input("alignment-textsize-slider", "value")],
)
def customize_textsize(val):
    return val


@app.callback(
    Output("alignment-chart", "correctgap"),
    [Input("alignment-correctgap-radio", "value")],
)
def customize_correctgap(val):
    return val


@app.callback(
    Output("alignment-chart", "data"),
    Output("alignment-field", "style"),
    Input("build-tree-button", "n_clicks"),
)
def update_alignment(click):
    if click == 0:
        raise PreventUpdate
    else:
        # TODO Load alignment
        with open() as fin:
            data = fin.read()
    return data, {"visibility": "visible"}
