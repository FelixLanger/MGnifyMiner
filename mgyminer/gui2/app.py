from mgyminer.gui2.utils.data_singleton import DataSingleton
import argparse

parser = argparse.ArgumentParser(description="Run the Dash app with specified input files.")
parser.add_argument("--query", type=str, help="Path to the query file.")
parser.add_argument("--hit_sequences", type=str, help="Path to the hit sequences file.")
parser.add_argument("--search_out", type=str, help="Path to the search output CSV file.")

args = parser.parse_args()

search_results = DataSingleton(
    data_path=args.search_out,
    query_file=args.query,
    hit_sequences=args.hit_sequences,
)


from mgyminer.gui2.server import app
from mgyminer.gui2.layouts import main_layout
from mgyminer.gui2.callbacks import (
    page_routing,
    scatter_callbacks,
    metadata_callbacks,
    filter_callbacks,
    phylogeny_callbacks,
    # alignment_callbacks,
)

app.layout = main_layout.layout

if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
