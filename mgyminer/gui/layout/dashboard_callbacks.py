import math
import tempfile
from collections import Counter
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from Bio import Phylo
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from gui.index import app

# tree imports
from mgyminer.phyltree import esl_sfetcher, fastTree, hmmaligner, hmmbuilder
from mgyminer.proteinTable import proteinTable


@app.callback(
    Output("stats-scatter", "figure"),
    Input("data-storage", "data"),
    Input("scatter-xaxis", "value"),
    Input("scatter-yaxis", "value"),
)
def update_scatter(data, xaxis_column_name, yaxis_column_name):
    if not data:
        return px.scatter()
    if xaxis_column_name == "e-value":
        log_x = True
    else:
        log_x = False

    if yaxis_column_name == "e-value":
        log_y = True
    else:
        log_y = False
    fig = px.scatter(
        data,
        x=xaxis_column_name,
        y=yaxis_column_name,
        hover_name="target_name",
        marginal_x="histogram",
        marginal_y="histogram",
        log_x=log_x,
        log_y=log_y,
    )
    fig.update_xaxes(title=xaxis_column_name)
    fig.update_yaxes(title=yaxis_column_name)
    fig.update_layout(clickmode="event+select")
    return fig


@app.callback(
    Output("data-storage", "data"),
    Input("submit-filter", "n_clicks"),
    Input("files-button", "n_clicks"),
    State("csv-input-dropdown", "value"),
    State("e-value-min", "value"),
    State("e-value-max", "value"),
    State("identity-min", "value"),
    State("identity-max", "value"),
    State("similarity-min", "value"),
    State("similarity-max", "value"),
)
def load_storage(
    click,
    click2,
    filepath,
    e_val_min,
    e_val_max,
    ident_min,
    ident_max,
    sim_min,
    sim_max,
):
    if filepath:
        pt = proteinTable(filepath)
        if any((e_val_min, e_val_max)):
            pt = pt.threshold("e-value", **threshold_kwargs(e_val_min, e_val_max))
        if any((ident_min, ident_max)):
            pt = pt.threshold("identity", **threshold_kwargs(ident_min, ident_max))
        if any((sim_min, sim_max)):
            pt = pt.threshold("similarity", **threshold_kwargs(sim_min, sim_max))
        return pt.df.to_dict()
    else:
        return {}


def threshold_kwargs(greater, less):
    kwargs = {}
    if greater:
        kwargs["greater"] = greater
    if less:
        kwargs["less"] = less
    return kwargs


@app.callback(
    Output("completeness", "figure"),
    Input("data-storage", "data"),
    Input("stats-scatter", "selectedData"),
)
def update_pie(data, selectedData):
    if not data:
        return px.scatter()
    pt = proteinTable(pd.DataFrame(data))
    if selectedData:
        indices = [int(e["pointIndex"]) for e in selectedData["points"]]
        dff = pt.df.iloc[indices]
    else:
        dff = pt.df
    fig = piecharts(dff)
    return fig


def piecharts(df):
    # Setup for prettier plots
    hole = 0.3
    textinfo = "label+percent"
    pretty_labels = {
        "FL": {
            "00": "full length",
            "11": "fragment",
            "01": "partial right",
            "10": "partial left",
            None: "not found",
        },
        "UP": {"0": "not in Uniprot", "1": "in Uniprot"},
        "CR": {"0": "Member", "1": "Representative"},
    }

    def _value_dist(column):
        counts = Counter(column)
        return {"labels": list(counts.keys()), "values": list(counts.values())}

    # Prepare for each plot
    fragments_data = _value_dist(df["FL"])
    fragments_data["labels"] = [
        pretty_labels["FL"][i] for i in fragments_data["labels"]
    ]
    fragments = go.Pie(**fragments_data, hole=hole, textinfo=textinfo, visible=True)

    # uniprot_data = _value_dist(df["UP"])
    # uniprot_data["labels"] = [pretty_labels["UP"][i] for i in uniprot_data["labels"]]
    # uniprot = go.Pie(**uniprot_data, hole=hole, textinfo=textinfo, visible=False)
    #
    # representative_data = _value_dist(df["CR"])
    # representative_data["labels"] = [
    #     pretty_labels["CR"][i] for i in representative_data["labels"]
    # ]
    # reps = go.Pie(**representative_data, hole=hole, textinfo=textinfo, visible=False)

    # Create Figure
    fig = go.Figure()
    fig.add_traces(
        [
            fragments
            # , uniprot, reps
        ]
    )
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list(
                    [
                        dict(
                            label="Completeness",
                            method="update",
                            args=[
                                {"visible": [True, False, False]},
                                {"title": "Protein Completeness"},
                            ],
                        ),
                        # dict(
                        #     label="Uniprot",
                        #     method="update",
                        #     args=[
                        #         {"visible": [False, True, False]},
                        #         {"title": "Uniprot"},
                        #     ],
                        # ),
                        # dict(
                        #     label="Cluster",
                        #     method="update",
                        #     args=[
                        #         {"visible": [False, False, True]},
                        #         {"title": "Clustering"},
                        #     ],
                        # ),
                    ]
                ),
            )
        ]
    )
    fig.update_layout(autosize=True, title="Completeness")
    return fig


@app.callback(
    Output("biome", "figure"),
    Input("data-storage", "data"),
    Input("stats-scatter", "selectedData"),
)
def update_biome(data, selectedData):
    if not data:
        return px.scatter()
    pt = proteinTable(pd.DataFrame(data))
    if selectedData:
        indices = [int(e["pointIndex"]) for e in selectedData["points"]]
        dff = pt.df.iloc[indices]
    else:
        dff = pt.df
    fig = biome_distribution(dff)
    return fig


def biome_distribution(df):
    biome_list = df["biome"].fillna("root:unknown").to_list()
    bl = []
    delim = "root:"
    for i in biome_list:
        bl.extend([delim + e for e in i.split(delim) if e])

    data = {}
    for biome in bl:
        split = biome.split(":")

        for i, s in enumerate(split):
            id = "-".join(split[: i + 1])
            if id in data:
                data[id]["counts"] = data[id]["counts"] + 1
            else:
                #                parent_index = i - 1
                data[id] = {
                    "counts": 1,
                    "label": s,
                    "id": id,
                    "parent": "-".join(split[:i]),
                }

    biome_counts = pd.DataFrame(data).transpose()
    biome_counts.drop("root", inplace=True)
    biome_counts.replace("root", "", inplace=True)

    fig = go.Figure(
        go.Sunburst(
            labels=biome_counts.label,
            parents=biome_counts.parent,
            values=biome_counts.counts,
            ids=biome_counts.id,
            branchvalues="total",
        )
    )
    fig.update_layout(autosize=True, title="Biome Distribution")
    return fig


@app.long_callback(
    output=Output("tree", "figure"),
    inputs=[
        Input("build-tree-button", "n_clicks"),
        State("data-storage", "data"),
        State("stats-scatter", "selectedData"),
        State("queryfasta-input-dropdown", "value"),
        State("sequences-input-dropdown", "value"),
    ],
    running=[
        (Output("build-tree-button", "disabled"), True, False),
        (Output("cancel-tree-button", "disabled"), False, True),
        (
            Output("tree-field", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            Output("progress_bar", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    cancel=[Input("cancel-tree-button", "n_clicks")],
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
    prevent_initial_call=True,
)
def build_tree(set_progress, n_clicks, data, selectedData, queryfasta, sequences):
    if not data:
        return px.scatter()
    i = 0
    total = 5
    set_progress((str(i), str(total)))
    pt = proteinTable(pd.DataFrame(data))
    if selectedData:

        indices = [int(e["pointIndex"]) for e in selectedData["points"]]
        dff = pt.df.iloc[indices]
    else:
        dff = pt.df
    dff.to_csv("last_selected.csv")
    i += 1
    set_progress((str(i), str(total)))
    tree_out = "selection.tree"
    tree = treebuilder(dff, queryfasta, tree_out)
    i += 1
    set_progress((str(i), str(total)))
    tree.make_alignment()
    i += 1
    set_progress((str(i), str(total)))
    tree.build_tree()
    i += 1
    set_progress((str(i), str(total)))
    f = plot_tree(dff, tree_out)
    i += 1
    set_progress((str(i), str(total)))
    return f


class treebuilder:
    def __init__(self, proteins, query, tree_out) -> None:
        self.input = proteins
        self.fetcher = esl_sfetcher()
        self.aligner = hmmaligner()
        self.hmmbuilder = hmmbuilder()
        self.query = query
        self.tree = tree_out
        self.alignment = Path("tree.afa")

    def make_alignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            keyfile = "keyfile"  # Path(tmpdir) /
            sequences = "sequences"  # Path(tmpdir) /
            hmm = Path(tmpdir) / "hmm"
            seq_df = self.input

            def _idpluscoords(row):
                if row["ndom"] > 1:
                    domain = "_" + str(row["ndom"])
                else:
                    domain = ""
                return f"{row['target_name']}{domain}/{row['env_from']}-{row['env_to']}"

            seq_df["dom_acc"] = seq_df.apply(lambda row: _idpluscoords(row), axis=1)
            seq_df[["dom_acc", "env_from", "env_to", "target_name"]].to_csv(
                keyfile, index=False, header=False, sep=" "
            )
            self.fetcher.run(
                "/home/felix/PycharmProjects/MGnifyMiner/playground/"
                "2022-09-27-MGnifyMiner_phmmer/ENTEROCIN/all_seqs.fa",
                namefile=keyfile,
                outfile=sequences,
                args=["-Cf"],
            )
            self.hmmbuilder.run(hmm, self.query)
            # Append query sequence to the alignment to add it to the tree
            with open(sequences, "at") as fout, open(self.query, "rt") as fin:
                fout.write(fin.read())
            self.aligner.run(hmm, self.alignment, sequences, outformat="afa")

    def build_tree(self) -> Path:
        ft = fastTree()
        ft.run(self.alignment, self.tree)


# @app.callback(
#     Output('table', 'data'),
#     Input('stats-scatter', 'selectedData'))
# def display_selected_data(selectedData):
#     if selectedData:
#         indices = [p['hovertext'] for p in selectedData['points']]
#     else:
#         indices = df["Name"]
#     subsetData = df[df["Name"].isin(indices)].to_dict('records')
#
#     return subsetData


def plot_tree(df, treefile):
    metadata = df
    tree = Phylo.read(treefile, "newick")

    def _idpluscoords(row):
        if row["ndom"] > 1:
            domain = "_" + str(row["ndom"])
        else:
            domain = ""
        return f"{row['target_name']}{domain}/{row['env_from']}-{row['env_to']}"

    metadata["dom_acc"] = metadata.apply(lambda row: _idpluscoords(row), axis=1)
    query = metadata["query_name"].iloc[0]

    minimum = 0
    maximum = math.inf
    #
    # if args.param is not None:
    #     # if parameter is specified find proteins that match filter for parameter
    #     filter_dict = _filter_dict(metadata, args.param)
    #     of_interest = _in_thresholds(filter_dict, minimum, maximum)
    # else:
    #     # if no parameter is given take the tree distance
    filter_dict = distances(tree, query)
    of_interest = _in_thresholds(filter_dict, minimum, maximum)

    x_coords = get_x_coordinates(tree)
    y_coords = get_y_coordinates(tree)

    line_shapes = []
    draw_clade(
        x_coords,
        y_coords,
        tree.root,
        0,
        line_shapes,
        line_color="rgb(25,25,25)",
        line_width=1,
    )

    my_tree_clades = x_coords.keys()
    X = []  # list of nodes x-coordinates
    Y = []  # list of nodes y-coords
    text = []  # list of text to be displayed on hover over nodes

    for cl in my_tree_clades:
        X.append(x_coords[cl])
        Y.append(y_coords[cl])
        text.append(cl.name)

    intermediate_node_color = "rgb(100,100,100)"
    color = [intermediate_node_color] * len(X)

    for index, row in metadata.iterrows():
        i = text.index(f"{row['dom_acc']}")
        if text[i] in of_interest:
            color[i] = "rgb(0, 200, 20)"
        text[i] = (
            text[i]
            + f"<br>Hit Coverage: {row['coverage_hit']}\
                              <br>Query Coverage: {row['coverage_query']}\
                              <br>Similarity: {row['similarity']}\
                              <br>Identity: {row['identity']}"
        )

    # color query in red
    i = text.index(query)
    color[i] = "rgb(200,0,0)"

    nodes = dict(
        type="scatter",
        x=X,
        y=Y,
        mode="markers",
        marker=dict(color=color, size=9),
        opacity=1.0,
        text=text,
        hoverinfo="text",
    )

    if "Pfams" in metadata.columns:
        # Choose color scheme for protein domains
        protein_ys = {}

        for node in range(0, len(nodes["x"])):
            if nodes["text"][node]:
                protein_ys[nodes["text"][node].split("<br>")[0]] = nodes["y"][node]

        smallest_y_dist(protein_ys)

        shapedata = {
            "type": [],
            "x0": [],
            "y0": [],
            "x1": [],
            "y1": [],
            "fillcolor": [],
            "layer": [],
            "line_width": [],
        }

        dom_hover_x = []
        dom_hover_y = []
        dom_hover_fill = []
        dom_hover_text = []

        # Build mapping of Pfam accs to domain name
        dom_names = dom_names = [
            name
            for arch in metadata["domain_names"].tolist()
            if isinstance(arch, str)
            for name in arch.split("~")
        ]
        dom_accs = [
            name
            for arch in metadata["Pfams"].tolist()
            if isinstance(arch, str)
            for name in arch.split("-")
        ]
        acc_to_name = dict(zip(dom_accs, dom_names))

        # Dict with protein and its domains
        pfams = _filter_dict(metadata, "Pfams")
        pfams = {k: v.split("-") for k, v in pfams.items()}
        # Get unique pfam domains in all hits
        unique_domains = set(
            [domain for domains in list(pfams.values()) for domain in domains]
        )

        baseline = domain_start(x_coords)
        smallest_y = smallest_y_dist(protein_ys)
        y_gap = smallest_y / 10
        half_height = (smallest_y - y_gap) / 2

        # domain section shouldnt take more than 1/3 of the plot size,
        # assuming we dont find more than 10 domains for a normal protein
        domain_width = (baseline / 3) / 10
        x_gab = domain_width / 2

        # dict with distinc color for each unique pfam
        pfam_colors = domain_colors(unique_domains)

        for protein in protein_ys.keys():
            start = baseline
            if protein == query:
                pass
            else:
                # Draw domain by domain
                for domain in pfams[protein]:
                    # Draw shape
                    x0 = start
                    x1 = start + domain_width
                    y0 = protein_ys[protein] - half_height
                    y1 = protein_ys[protein] + half_height
                    shapedata["type"].append("rect")
                    shapedata["x0"].append(x0)
                    shapedata["y0"].append(y0)
                    shapedata["x1"].append(x1)
                    shapedata["y1"].append(y1)
                    shapedata["fillcolor"].append(pfam_colors[domain])
                    shapedata["layer"].append("above")
                    shapedata["line_width"].append(0)

                    # Draw invisible glyph for hover info
                    dom_hover_x.append([x0, x1, x1, x0, x0])
                    dom_hover_y.append([y0, y0, y1, y1, y0])
                    dom_hover_fill.append(pfam_colors[domain])
                    dom_hover_text.append(
                        f"<br>Pfam Accession: {domain} <br>Name: {acc_to_name[domain]}"
                    )

                    start = start + domain_width + x_gab
                # Add a straight line to conncect domains
                shapedata["type"].append("rect")
                shapedata["x0"].append(baseline + x_gab)
                shapedata["y0"].append(protein_ys[protein])
                shapedata["x1"].append(start - (domain_width + x_gab))
                shapedata["y1"].append(protein_ys[protein])
                shapedata["fillcolor"].append("black")
                shapedata["layer"].append("below")
                shapedata["line_width"].append(5)  # Might need to be variable

        domain_shapes = [
            go.layout.Shape(
                type=shapedata["type"][i],
                x0=shapedata["x0"][i],
                x1=shapedata["x1"][i],
                y0=shapedata["y0"][i],
                y1=shapedata["y1"][i],
                fillcolor=shapedata["fillcolor"][i],
                opacity=1,
                layer=shapedata["layer"][i],
                line_width=shapedata["line_width"][i],
            )
            for i in range(len(shapedata["x0"]))
        ]
        shapes = line_shapes + domain_shapes

        dom_hover_data = dict(
            type="scatter",
            fill="toself",
            x=dom_hover_x,
            y=dom_hover_y,
            mode="lines",
            name="",
            opacity=1,
            fillcolor=dom_hover_fill,
            text=dom_hover_text,
            hoverinfo="text",
        )

    else:
        shapes = line_shapes

    layout = dict(
        title=f"Phylogeny of {query} against MGnify proteins",
        font=dict(family="Balto", size=14),
        width=800,
        height=800,
        autosize=False,
        showlegend=False,
        xaxis=dict(
            showline=True,
            zeroline=False,
            showgrid=False,
            ticklen=4,
            showticklabels=True,
            title="branch length",
        ),
        yaxis=dict(visible=False),
        hovermode="closest",
        plot_bgcolor="rgb(250,250,250)",
        margin=dict(l=10),
        shapes=shapes,  # lines for tree branches
    )
    f = go.Figure(data=[nodes], layout=layout)

    if "Pfams" in metadata.columns:
        for i in range(len(dom_hover_data["text"])):
            f.add_trace(
                go.Scatter(
                    x=dom_hover_data["x"][i],
                    y=dom_hover_data["y"][i],
                    fill="toself",
                    mode="lines",
                    name="",
                    text=dom_hover_data["text"][i],
                    opacity=0,
                    fillcolor=dom_hover_data["fillcolor"][i],
                )
            )

    return f


def get_x_coordinates(tree):
    # Associates to  each clade a x-coord.
    # returns a dict {clade: x-coord}, i.e the key is a clade, and x-coord its value

    xcoords = tree.depths()
    # tree.depth() maps tree clades to depths (by branch length).
    # returns a dict {clade: depth} where clade runs over all Clade instances of the tree,
    # and depth is the distance from root to clade

    # If there are no branch lengths, assign unit branch lengths
    if not max(xcoords.values()):
        xcoords = tree.depths(unit_branch_lengths=True)
    return xcoords


def get_y_coordinates(tree, dist=1.3):
    # y-coordinates are   multiple of dist (i*dist below);
    # dist: vertical distance between two consecutive leafs; it is chosen such that to get a tree of
    # reasonable height
    # returns  a dict {clade: y-coord}

    maxheight = tree.count_terminals()  # Counts the number of tree leafs.

    ycoords = dict(
        (leaf, maxheight - i * dist)
        for i, leaf in enumerate(reversed(tree.get_terminals()))
    )

    def calc_row(clade):
        for subclade in clade:
            if subclade not in ycoords:
                calc_row(subclade)
        ycoords[clade] = (ycoords[clade.clades[0]] + ycoords[clade.clades[-1]]) / 2

    if tree.root.clades:
        calc_row(tree.root)
    return ycoords


def get_clade_lines(
    orientation="horizontal",
    y_curr=0,
    x_start=0,
    x_curr=0,
    y_bot=0,
    y_top=0,
    line_color="rgb(25,25,25)",
    line_width=0.5,
):
    # define a Plotly shape of type 'line', for each branch

    branch_line = dict(
        type="line", layer="below", line=dict(color=line_color, width=line_width)
    )
    if orientation == "horizontal":
        branch_line.update(x0=x_start, y0=y_curr, x1=x_curr, y1=y_curr)
    elif orientation == "vertical":
        branch_line.update(x0=x_curr, y0=y_bot, x1=x_curr, y1=y_top)
    else:
        raise ValueError("Line type can be 'horizontal' or 'vertical'")

    return branch_line


def draw_clade(
    x_coords,
    y_coords,
    clade,
    x_start,
    line_shapes,
    line_color="rgb(15,15,15)",
    line_width=1,
):
    # defines recursively  the tree  lines (branches), starting from the argument clade

    x_curr = x_coords[clade]
    y_curr = y_coords[clade]

    # Draw a horizontal line
    branch_line = get_clade_lines(
        orientation="horizontal",
        y_curr=y_curr,
        x_start=x_start,
        x_curr=x_curr,
        line_color=line_color,
        line_width=line_width,
    )

    line_shapes.append(branch_line)

    if clade.clades:
        # Draw a vertical line connecting all children
        y_top = y_coords[clade.clades[0]]
        y_bot = y_coords[clade.clades[-1]]

        line_shapes.append(
            get_clade_lines(
                orientation="vertical",
                x_curr=x_curr,
                y_bot=y_bot,
                y_top=y_top,
                line_color=line_color,
                line_width=line_width,
            )
        )

        # Draw descendants
        for child in clade:
            draw_clade(x_coords, y_coords, child, x_curr, line_shapes)


def distances(tree, target):
    if isinstance(target, str):
        target = [i for i in tree.find_elements(target)][0]
    closest = {
        terminal.name: tree.distance(target, terminal)
        for terminal in tree.get_terminals()
    }
    closest = {k: v for k, v in sorted(closest.items(), key=lambda item: item[1])}
    return closest


def _in_thresholds(paramdict, threshold_min=0, threshold_max=math.inf):
    """
    Return all dictionary entries, which have a values between threshold_min and threshold_max
    :param paramdict:
    :param threshold_min:
    :param threshold_max:
    :return:
    """
    x = [
        key
        for key, value in paramdict.items()
        if value > threshold_min and value < threshold_max
    ]
    return x


def _filter_dict(metadata, parameter):
    """Efficient way to make a dict from two dataframe columns https://stackoverflow.com/questions/17426292/"""
    return pd.Series(list(metadata[parameter]), index=metadata["dom_acc"]).to_dict()


def domain_colors(domains):
    """
    function to create a domain : color dictionary. The colors will be based on
    the dark24 color palette. If the number of domains is greater than the length
    of the palette the colors will start again from the beginning.
    :param domains:
    :return:
    """
    # color palette from plotly 10 colors, if more are needed dark24
    palette = px.colors.qualitative.D3
    domains = set(domains)
    colors = []
    for i in range(len(domains)):
        colors.append(palette[(i) % len(palette)])
    return dict(zip(domains, colors))


def domain_start(x_coords):
    return max(x_coords.values()) + 0.5


def smallest_y_dist(protein_ys):
    ys = sorted(protein_ys.values())
    prev = ys[0]
    smallest_dist = math.inf
    for y in ys[1:]:
        dist = abs(prev - y)
        if smallest_dist > dist:
            smallest_dist = dist
        prev = y
    return smallest_dist


# Alignment Callbacks


def alignment_callbacks(_app):
    @_app.callback(
        Output("alignment-chart", "overview"),
        Input("alignment-overview-dropdown", "value"),
    )
    def customize_overview(val):
        return val

    @_app.callback(
        Output("alignment-chart", "showconsensus"),
        [Input("alignment-showconsensus-radio", "value")],
    )
    def customize_showconsensus(val):
        return val

    @_app.callback(
        Output("alignment-chart", "showconservation"),
        [Input("alignment-showconservation-radio", "value")],
    )
    def customize_showconservation(val):
        return val

    @_app.callback(
        Output("alignment-chart", "showgap"),
        [Input("alignment-showgap-radio", "value")],
    )
    def customize_showgap(val):
        return val

    @_app.callback(
        Output("alignment-chart", "textsize"),
        [Input("alignment-textsize-slider", "value")],
    )
    def customize_textsize(val):
        return val

    @_app.callback(
        Output("alignment-chart", "data"),
        Output("alignment-field", "style"),
        Input("alignment-button", "n_clicks"),
        State("alignment-input-dropdown", "value"),
    )
    def update_alignment(click, path):
        if click == 0:
            raise PreventUpdate
        else:
            with open(path, "rt") as fin:
                data = fin.read()
        return data, {"visibility": "visible"}
