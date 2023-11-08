from mgyminer.gui2.utils.data_singleton import DataSingleton

search_results = DataSingleton("../../local_tests/run/output.csv")

from mgyminer.gui2.server import app
from mgyminer.gui2.layouts import main_layout
from mgyminer.gui2.callbacks import (
    page_routing,
    scatter_callbacks,
    metadata_callbacks,
    filter_callbacks,
)

app.layout = main_layout.layout

if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
