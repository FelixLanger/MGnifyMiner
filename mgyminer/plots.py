import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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


def minimum_difference(lst):
    """
    Calculate the smallest difference between all elements in list lst.
    :param lst: list of numbers
    :return diff: smallest difference between two points in list
    """
    lst = sorted(lst)
    diff = math.inf

    for i in range(len(lst) - 1):
        if lst[i + 1] - lst[i] < diff:
            diff = lst[i + 1] - lst[i]
    return diff


def df_to_dict(key_column, value_column):
    """Efficient way to make a dict from two dataframe columns
    https://stackoverflow.com/questions/17426292/"""
    return pd.Series(value_column.values, index=key_column).to_dict()


def domain_colors(domains):
    """
    function to create a domain : color dictionary. The colors will be based on
    the D3 and dark24 color palette. If the number of domains is greater than the length
    of the palette the colors will start again from the beginning.
    :param domains:
    :return:
    """
    palette = px.colors.qualitative.D3 + px.colors.qualitative.Dark24
    domains = set(domains)
    colors = []
    for i in range(len(domains)):
        colors.append(palette[(i) % len(palette)])
    return dict(zip(domains, colors))


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


def phylogenetic_tree(
    tree=None,
    metadata=None,
    domain_data=None,
    reference=False,
    reference_color="rgb(200,0,0)",
    default_color="rgb(0, 200, 20)",
):
    # Get coordinates of terminals and branches in tree
    x_coords = get_x_coordinates(tree)
    y_coords = get_y_coordinates(tree)

    # Define lines to connect tree elements
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

    plot_info = {}

    for cl in my_tree_clades:
        plot_info[cl.name] = {
            "x": x_coords[cl],
            "y": y_coords[cl],
            "text": cl.name,
            "color": default_color,
        }

    if reference:
        plot_info[reference]["color"] = reference_color

    X = [i["x"] for i in plot_info.values()]
    Y = [i["y"] for i in plot_info.values()]
    text = [i["text"] for i in plot_info.values()]
    color = [i["color"] for i in plot_info.values()]

    if metadata:
        for row in metadata.itertuples():
            plot_info[metadata.target_name]["text"] = (
                plot_info[metadata.target_name]["text"]
                + f"<br>Hit Coverage: {row.coverage_hit}\
                                  <br>Query Coverage: {row.coverage_query}\
                                  <br>Similarity: {row.similarity}\
                                  <br>Identity: {row.identity}"
            )

    tree_trace = dict(
        type="scatter",
        x=X,
        y=Y,
        mode="markers",
        marker=dict(color=color, size=5),
        opacity=1.0,
        text=text,
        hoverinfo="text",
        xaxis="x",
        yaxis="y",
    )
    layout = dict(
        # title=f"Phylogeny of against MGnify proteins",
        # font=dict(family="Balto", size=14),
        width=800,
        height=800,
        # autosize=True,
        # showlegend=False,
        xaxis=dict(
            showline=True,
            zeroline=False,
            showgrid=False,
            ticklen=4,
            showticklabels=True,
            title="branch length",
            domain=[0, 1],
        ),
        yaxis=dict(visible=False),
        hovermode="closest",
        plot_bgcolor="rgb(250,250,250)",
        margin=dict(l=100),
        shapes=line_shapes,  # lines for tree branches
    )

    # If dataframe with domain annotations is provided, extend the plot with domain visualisation

    fig = go.Figure(data=[tree_trace], layout=layout)

    return fig
