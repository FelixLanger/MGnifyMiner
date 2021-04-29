import math

import pandas as pd
import plotly.graph_objects as go
from Bio import Phylo


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
    """ Efficient way to make a dict from two dataframe columns https://stackoverflow.com/questions/17426292/"""
    return pd.Series(list(metadata[parameter]), index=metadata["dom_acc"]).to_dict()


def plot_tree(args):
    metadata = pd.read_csv(args.filter)
    tree = Phylo.read(args.tree, "newick")

    def _idpluscoords(row):
        if row["ndom"] > 1:
            domain = "_" + str(row["ndom"])
        else:
            domain = ""
        return f"{row['target_name']}{domain}/{row['env_from']}-{row['env_to']}"

    metadata["dom_acc"] = metadata.apply(lambda row: _idpluscoords(row), axis=1)
    # TODO find way to get the name of the query sequence not from arguments but somewhere else to reduce number
    #  of flags
    query = args.query

    min = 0 if args.min is None else args.min
    max = math.inf if args.max is None else args.max

    if "param" in dir(args):
        # if parameter is specified find proteins that match filter for parameter
        filter_dict = _filter_dict(metadata, args.param)
        of_interest = _in_thresholds(filter_dict, min, max)
    else:
        # if no parameter is given take the tree distance
        filter_dict = distances(tree, query)
        of_interest = _in_thresholds(filter_dict, min, max)

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
        shapes=line_shapes,  # lines for tree branches
    )
    f = go.Figure(data=[nodes], layout=layout)
    f.write_html("tree_vis.html")
