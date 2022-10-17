import dash_bootstrap_components as dbc
import diskcache
from dash import Dash
from dash.long_callback import DiskcacheLongCallbackManager

external_stylesheets = [dbc.themes.SANDSTONE]

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
    long_callback_manager=long_callback_manager,
)
app_title = "MGnifyMiner"
app.title = app_title
