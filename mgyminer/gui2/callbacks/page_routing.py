from dash.dependencies import Input, Output
from mgyminer.gui2.app import app
from mgyminer.gui2.layouts.homepage import page


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return page
    # elif pathname == "/page-1":
    #     return "This is the content of page 1. Yay!"
    # elif pathname == "/page-2":
    #     return "Oh cool, this is page 2!"
    # If the user tries to reach a different page, return a 404 message
    return [
        "404: Not found",
        f"The pathname {pathname} was not recognised...",
    ]
