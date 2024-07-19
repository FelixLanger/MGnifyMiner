import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative


def create_genome_plot(
    data,
    names,
    color_col=None,
    pattern_col=None,
    title="Genome Plot",
    sequence_length=None,
    show_legend=True,
    color_map=None,
    pattern_shape_map=None,
    palette=qualitative.Plotly,
    shape_height=0.2,
    **layout_kwargs,
):
    data = data.copy()

    data["start"] = data["start"].astype(int)
    data["stop"] = data["stop"].astype(int)

    data["strand"] = data["strand"].map({"+": 1, "-": -1}).astype(int)

    data = assign_levels(data)

    if not sequence_length:
        sequence_length = max(data["stop"])

    if color_col in data.columns:
        unique_features = sorted(data[color_col].unique())
        if color_map is None:
            color_map = {feature: palette[i % len(palette)] for i, feature in enumerate(unique_features)}
    else:
        default_color = palette[0]
        color_map = {None: default_color}

    fill_pattern_shapes = ["", "/", "\\", "x", "-", "|", "+", "."]
    if pattern_col in data.columns:
        unique_secondary_features = sorted(data[pattern_col].unique())
        if pattern_shape_map is None:
            pattern_shape_map = {
                feature: fill_pattern_shapes[i % len(fill_pattern_shapes)]
                for i, feature in enumerate(unique_secondary_features)
            }
    else:
        pattern_shape_map = None

    data[["xs", "ys"]] = data.apply(
        lambda x: pd.Series(
            create_trace_data(
                x["start"],
                x["stop"],
                x["strand"],
                level=x["level"],
                height=shape_height,
            )
        ),
        axis=1,
    )

    traces = []
    legend_added = set()

    for _, row in data.iterrows():
        color = color_map.get(row.get(color_col), palette[0])  # Use the specified color or default color
        show_in_legend = row.get(color_col) not in legend_added
        if show_in_legend:
            legend_added.add(row.get(color_col))

        fill_pattern = pattern_shape_map.get(row.get(pattern_col), None) if pattern_col in data.columns else None

        trace = go.Scatter(
            x=row["xs"],
            y=row["ys"],
            fill="toself",
            mode="lines",
            line=dict(color=color, width=1),
            fillcolor=color,
            fillpattern=dict(shape=fill_pattern) if fill_pattern else None,
            hoverinfo="text",
            text=row[names],
            name=row.get(color_col),
            legendgroup=row.get(color_col),
            showlegend=show_in_legend,
        )
        traces.append(trace)

    # Calculate spacing of the feature borders to the axes
    x_spacing = sequence_length * 0.02
    max_level = data["level"].max()
    # 1.5 is default level_spacing in create_trace_data
    # should be made dynamic incase level_spacing is exposed
    y_top = (max_level * shape_height * 1.5) + 2 * shape_height
    y_bot = -(2 * shape_height)

    layout = go.Layout(
        title=title,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            range=[-x_spacing, sequence_length + x_spacing],
        ),
        yaxis=dict(showgrid=False, zeroline=False, range=[y_bot, y_top], visible=False),
        showlegend=show_legend and (color_col in data.columns),
        shapes=[
            dict(
                type="line",
                x0=0,
                y0=0,
                x1=sequence_length,
                y1=0,
                line=dict(color="black", width=4),
                layer="below",
            )
        ],
        **layout_kwargs,
    )

    fig = go.Figure(data=traces, layout=layout)
    return fig


def create_trace_data(
    start,
    end,
    strand,
    height=0.2,
    level=0,
    level_spacing=1.5,  # Controls the vertical spacing between levels
    arrow_prop=0.15,  # Proportion of the arrow head to the total length
):
    h = height / 2.0
    x1, x2 = (start, end) if strand >= 0 else (end, start)

    arrow_length = abs(x2 - x1)
    delta = arrow_length * arrow_prop

    head_base = max(x1, x2 - delta) if strand >= 0 else min(x1, x2 + delta)

    level_offset = level * height * level_spacing
    ys = [
        level_offset - h,
        level_offset + h,
        level_offset + h,
        level_offset,
        level_offset - h,
        level_offset - h,
    ]
    xs = [x1, x1, head_base, x2, head_base, x1]
    return xs, ys


def assign_levels(data):
    start_events = pd.DataFrame({"position": data["start"], "change": 1, "index": data.index})
    stop_events = pd.DataFrame({"position": data["stop"] + 1, "change": -1, "index": data.index})
    events = pd.concat([start_events, stop_events]).sort_values(by=["position", "change"], ascending=[True, False])
    events["active_intervals"] = events["change"].cumsum()
    data["level"] = events.loc[events["change"] == 1, "active_intervals"] - 1
    return data
