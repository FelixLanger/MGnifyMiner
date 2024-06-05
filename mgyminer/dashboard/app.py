import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from callbacks.overview_callbacks import *
from callbacks.phylogeny_callbacks import *

from mgyminer.dashboard.utils.data_store import protein_store

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)


from mgyminer.proteintable import ProteinTable

# data = "/home/flx/PycharmProjects/multiminer/MultiMiner/prototyping/PA/mgnifyminer_results/WBR49958_mgy70sim_70qcov.csv"
data = "/home/flx/PycharmProjects/MGnifyMiner2/results/I6PHU9_mgy.csv"

protein_store.set_dataframe(ProteinTable(data))

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(f"{page['name']}", href=page["relative_path"])) for page in dash.page_registry.values()
    ],
    brand="🔬⛏️MGnify Protein Miner",
    brand_href="#",
    color="#18974c",
    dark=True,
    fluid=True,
    # style={"padding": "1rem"}
)


app.layout = html.Div(
    [
        navbar,
        dash.page_container,
        dcc.Store(id="filtered-data-store", data=None),
    ]
)


if __name__ == "__main__":
    app.run(debug=False)
