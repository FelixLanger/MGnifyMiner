import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative
from plotly.subplots import make_subplots


def get_x_coordinates(tree):
    """
    Calculates the x-coordinates of the nodes in a phylogenetic tree.
    Args:
        tree (Tree): A phylogenetic tree object.
    Returns:
        dict: A dictionary mapping each clade to its x-coordinate.
    """
    x_coords = tree.depths()
    if not max(x_coords.values()):
        x_coords = tree.depths(unit_branch_lengths=True)
    return x_coords


def get_y_coordinates(tree, dist=1):
    """
    Calculates the y-coordinates of the nodes in a phylogenetic tree.

    Args:
        tree (Tree): A phylogenetic tree object.
        dist (float, optional): The vertical distance between adjacent leaves. Default is 1.

    Returns:
        dict: A dictionary mapping each clade to its y-coordinate.

    Notes:
        The y-coordinates are assigned based on the order of the leaves in the tree.
        The root of the tree is positioned at the middle of its descendant leaves.
    """
    max_height = tree.count_terminals()
    y_coords = {leaf: max_height - i * dist for i, leaf in enumerate(reversed(tree.get_terminals()))}

    def calc_internal_node_y(clade):
        if not clade.is_terminal():
            for subclade in clade:
                calc_internal_node_y(subclade)
            y_coords[clade] = (y_coords[clade.clades[0]] + y_coords[clade.clades[-1]]) / 2

    calc_internal_node_y(tree.root)
    return y_coords


def get_clade_line(orientation, start, end, y=None, line_color="rgb(25,25,25)", line_width=1):
    """
    Creates a line shape for a clade in a phylogenetic tree.

    Args:
        orientation (str): The orientation of the line, either "horizontal" or "vertical".
        start (tuple): The starting coordinates of the line (x, y).
        end (tuple): The ending coordinates of the line (x, y).
        y (float, optional): The y-coordinate for a horizontal line. Required if orientation is "horizontal".
        line_color (str, optional): The color of the line. Default is "rgb(25,25,25)" (dark gray).
        line_width (float, optional): The width of the line. Default is 1.

    Returns:
        dict: A dictionary representing the line shape.

    Raises:
        ValueError: If the orientation is not "horizontal" or "vertical".
        ValueError: If the orientation is "horizontal" and y is not provided.
    """
    line = dict(type="line", layer="below", line=dict(color=line_color, width=line_width))

    if orientation == "horizontal":
        if y is None:
            raise ValueError("y-coordinate must be provided for horizontal lines")
        line.update(x0=start[0], y0=y, x1=end[0], y1=y)
    elif orientation == "vertical":
        line.update(x0=start[0], y0=start[1], x1=end[0], y1=end[1])
    else:
        raise ValueError("Orientation must be either 'horizontal' or 'vertical'")

    return line


def draw_clade(x_coords, y_coords, clade, x_start, line_shapes, line_color="black", line_width=1):
    """
    Recursively draws the lines for a clade and its descendants in a phylogenetic tree.

    Args:
        x_coords (dict): Dictionary mapping clades to their x-coordinates.
        y_coords (dict): Dictionary mapping clades to their y-coordinates.
        clade (Clade): The current clade being processed.
        x_start (float): The starting x-coordinate for the current clade's line.
        line_shapes (list): List to store the line shapes representing the clades.
        line_color (str, optional): The color of the clade lines. Default is black.
        line_width (float, optional): The width of the clade lines. Default is 1.

    Returns:
        None
    """
    x_curr = x_coords[clade]
    y_curr = y_coords[clade]

    line_shapes.append(
        get_clade_line("horizontal", (x_start, y_curr), (x_curr, y_curr), y_curr, line_color, line_width)
    )

    if clade.clades:
        y_top = y_coords[clade.clades[0]]
        y_bot = y_coords[clade.clades[-1]]
        line_shapes.append(get_clade_line("vertical", (x_curr, y_bot), (x_curr, y_top), None, line_color, line_width))

        for child in clade:
            draw_clade(x_coords, y_coords, child, x_curr, line_shapes, line_color, line_width)


def create_box_trace_coordinates(start, end, height, y):
    """
    Creates the coordinates for a box-shaped trace.

    Args:
        start (float): The starting x-coordinate of the box.
        end (float): The ending x-coordinate of the box.
        height (float): The height of the box.
        y (float): The y-coordinate of the center of the box.

    Returns:
        tuple: A tuple containing two lists:
            - xs (list): The x-coordinates of the box vertices.
            - ys (list): The y-coordinates of the box vertices.
    """
    half_height = height / 2
    xs = [start, end, end, start, start]
    ys = [y - half_height, y - half_height, y + half_height, y + half_height, y - half_height]
    return xs, ys


def create_trace(xs, ys, color, name, showlegend=False):
    """
    Creates a Plotly Scatter trace for a box-shaped object.

    Args:
        xs (list): The x-coordinates of the box vertices.
        ys (list): The y-coordinates of the box vertices.
        color (str): The color of the box fill and line.
        name (str): The name of the trace, used for hover text and legend.
        showlegend (bool, optional): Whether to show the trace in the legend. Default is False.

    Returns:
        go.Scatter: A Plotly Scatter trace representing the box-shaped object.
    """
    return go.Scatter(
        x=xs,
        y=ys,
        fill="toself",
        mode="lines",
        line=dict(color=color, width=1),
        fillcolor=color,
        hoverinfo="text",
        text=name,
        name=name,
        legendgroup=name,
        showlegend=showlegend,
    )


def prepare_domain_data(domain_architecture, y_mapping):
    """
    Prepares domain architecture data for plotting. The expexted input data should contain PF1-PF2 formated
    architecture strings.
    It performs the following steps:
        - remove duplicate domain architecture data for a given MGYP
        - Split pfam_architecture into individual domains
        - Explode the pfam_domains column to create a new row for each domain
        - Assign a unique index to each domain within each MGYP group
        - Calculate the start and stop coordinates for each domain
        - make only the first occurrence of a Pfam shown in legend (otherwise legend gets flooded with duplicates)
        - Assign y-coordinates to each target based on the y_mapping and calculate protein length
    Args:
        domain_architecture (pandas.DataFrame): DataFrame containing domain architecture information.
            Required columns: "pfam_architecture", "target_name".
        y_mapping (dict): Dictionary mapping target names to their corresponding y-coordinates.

    Returns:
        tuple: A tuple containing two DataFrames:
            - transformed_data (pandas.DataFrame): DataFrame with transformed domain data for plotting.
                Columns: "target_name", "start", "stop", "name", "showlegend", "y".
            - domain_architecture (pandas.DataFrame): Updated input DataFrame with an additional "len" column.

    """
    domain_architecture.drop_duplicates(subset="target_name", keep="first", inplace=True)
    domain_architecture["pfam_domains"] = domain_architecture["pfam_architecture"].str.split("-")
    exploded_data = domain_architecture.explode("pfam_domains")
    exploded_data["domain_index"] = exploded_data.groupby("target_name").cumcount() + 1
    exploded_data["start"] = (exploded_data["domain_index"] * 1.5) - 1.5
    exploded_data["stop"] = (exploded_data["domain_index"] * 1.5) - 0.5
    transformed_data = exploded_data[["target_name", "start", "stop", "pfam_domains"]].rename(
        columns={"pfam_domains": "name"}
    )
    transformed_data["showlegend"] = ~transformed_data["name"].duplicated()
    transformed_data["y"] = transformed_data["target_name"].map(y_mapping)
    domain_architecture["length"] = domain_architecture["pfam_domains"].apply(lambda x: len(x) + ((len(x) - 1) * 0.5))

    return transformed_data, domain_architecture


def assign_domain_colors(transformed_data, domain_colors):
    """
    Assigns colors to each unique domain in the transformed domain data.
    Args:
        transformed_data (pandas.DataFrame): DataFrame with transformed domain data.
            Required columns: "name".
        domain_colors (dict): Dictionary mapping domain names to colors.
            If a domain is not present in the dictionary, a color from the qualitative.Plotly colorscheme will be used.
    Returns:
        pandas.DataFrame: Updated transformed_data DataFrame with an additional "color" column.
    """
    unique_domains = sorted(transformed_data["name"].unique())
    plotly_colors = qualitative.Plotly
    color_map = {
        domain: domain_colors.get(domain, plotly_colors[i % len(plotly_colors)])
        for i, domain in enumerate(unique_domains)
    }
    transformed_data["color"] = transformed_data["name"].map(color_map)
    return transformed_data


def plot_tree(
    tree,
    domain_architecture=None,
    node_colors=None,
    hovertext=None,
    domain_colors=None,
    domain_spacing=0.7,
    line_color="black",
    line_width=1,
):
    """
    Plot a phylogenetic tree with optional domain architecture.

    Args:
        tree (Bio.Phylo.BaseTree.Tree): Phylogenetic tree object.
        domain_architecture (pandas.DataFrame, optional): DataFrame containing domain architecture data.
            Required columns: "target_name", "length", "start", "stop", "name".
        node_colors (dict, optional): Dictionary mapping MGYP accessions to node colors.
        hovertext (dict, optional): Dictionary mapping MGYP accessions to custom hover text.
        domain_colors (dict, optional): Dictionary mapping domain names to colors.
        domain_spacing (float, optional): Spacing factor between domains. Default is 0.7.
        line_color (str, optional): Color of the tree branches. Default is "black".
        line_width (int, optional): Width of the tree branches. Default is 1.

    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure object representing the tree and domain architecture.
    """
    smallest_y_difference = 1
    x_coords = get_x_coordinates(tree)
    y_coords = get_y_coordinates(tree, dist=smallest_y_difference)

    line_shapes = []
    draw_clade(x_coords, y_coords, tree.root, 0, line_shapes, line_color=line_color, line_width=line_width)

    terminal_clades = list(tree.get_terminals())
    x = [x_coords[cl] for cl in terminal_clades]
    y = [y_coords[cl] for cl in terminal_clades]
    node_name = [cl.name for cl in terminal_clades]
    y_mapping = {cl.name.split(":")[0]: y_coords[cl] for cl in terminal_clades}

    max_height = smallest_y_difference * domain_spacing

    default_color = "rgb(100,100,100)"
    color = [node_colors.get(node.split(":")[0], default_color) if node_colors else default_color for node in node_name]

    hovertext = [hovertext.get(node.split(":")[0], node) for node in node_name] if hovertext else node_name

    nodes = dict(
        type="scatter",
        x=x,
        y=y,
        mode="markers",
        marker=dict(color=color, size=9),
        opacity=1.0,
        text=hovertext,
        hoverinfo="text",
        showlegend=False,
    )

    if domain_architecture is None:
        fig = go.Figure(data=[nodes], layout=go.Layout(shapes=line_shapes))
    else:
        transformed_data, domain_architecture = prepare_domain_data(domain_architecture, y_mapping)
        transformed_data = assign_domain_colors(transformed_data, domain_colors or {})
        transformed_data[["xs", "ys"]] = transformed_data.apply(
            lambda x: pd.Series(create_box_trace_coordinates(x["start"], x["stop"], max_height, x["y"])), axis=1
        )

        fig = make_subplots(rows=1, cols=2, shared_yaxes=True, column_widths=[0.8, 0.2], horizontal_spacing=0.01)
        fig.add_trace(nodes, row=1, col=1)

        for _, row in transformed_data.iterrows():
            trace = create_trace(row["xs"], row["ys"], row["color"], row["name"], showlegend=row["showlegend"])
            fig.add_trace(trace, row=1, col=2)

        for _, row in domain_architecture.iterrows():
            line_shapes.append(
                dict(
                    type="line",
                    x0=0,
                    y0=y_mapping[row["target_name"]],
                    x1=row["length"],
                    y1=y_mapping[row["target_name"]],
                    line=dict(color="black", width=3),
                    layer="below",
                    xref="x2",
                    yref="y2",
                )
            )

    fig.update_layout(
        showlegend=True,
        xaxis=dict(
            showline=True,
            zeroline=False,
            showgrid=False,
            ticklen=4,
            showticklabels=True,
            title="Branch Length",
        ),
        yaxis=dict(visible=False),
        xaxis2=dict(
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
        ),
        yaxis2=dict(
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
        ),
        hovermode="closest",
        margin=dict(l=5, r=5, t=5, b=5),
        shapes=line_shapes,
    )

    return fig
