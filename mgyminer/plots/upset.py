import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def upset_plot(df, sorted_x=False, sorted_y=False):
    combination_dict = calculate_intersection_set_counts(df)
    targets_per_query = calculate_targets_per_query(df)

    if sorted_x:
        sorted_combinations = sorted(combination_dict.items(), key=lambda x: x[1], reverse=True)
    else:
        sorted_combinations = list(combination_dict.items())
    sorted_combo_names = [item[0] for item in sorted_combinations]

    if sorted_y:
        sorted_queries = sorted(targets_per_query.items(), key=lambda x: x[1], reverse=True)
    else:
        sorted_queries = list(targets_per_query.items())
    sorted_query_names = [item[0] for item in sorted_queries]

    x = []
    y = []

    for query in sorted_query_names:
        for combo in sorted_combo_names:
            if query in combo.split(", "):
                x.append(combo)
                y.append(query)

    # Create a figure with two subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{}, {}], [{}, {}]],
        shared_xaxes=True,
        shared_yaxes=True,
        column_widths=[0.35, 0.65],
        row_heights=[0.65, 0.35],
        vertical_spacing=0.02,
    )

    # Add intersecting counts bar chart (upper right)
    fig.add_trace(
        go.Bar(
            x=sorted_combo_names,
            y=[combination_dict[combo] for combo in sorted_combo_names],
            text=[combination_dict[combo] for combo in sorted_combo_names],
            texttemplate="%{text:}",
            textposition="outside",
            textfont_size=12,
            textangle=-90,
            cliponaxis=False,
            marker_line=dict(width=0.0),
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # Add absolute number of target_names bar chart (left)
    fig.add_trace(
        go.Bar(
            y=sorted_query_names,
            x=[targets_per_query[query] for query in sorted_query_names],
            text=[targets_per_query[query] for query in sorted_query_names],
            texttemplate="%{text:}",
            textposition="inside",
            textfont_size=12,
            textangle=0,
            cliponaxis=False,
            orientation="h",
            marker_line=dict(width=0.0),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # Add scatter plot (lower right)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            name="Query Combinations",
            marker=dict(
                line_width=0,
                color="#000000",
                line_color="#000000",
                symbol="circle",
                size=8,
            ),
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    # Add vertical lines
    for combo in sorted_combo_names:
        queries = [y[i] for i in range(len(x)) if x[i] == combo]
        if len(queries) > 1:
            y_min = min(queries)
            y_max = max(queries)
            fig.add_shape(
                type="line", x0=combo, x1=combo, y0=y_min, y1=y_max, line=dict(color="black", width=2), row=2, col=2
            )

    # Add grey rows
    for i in range(len(sorted_query_names)):
        if i % 2 == 0:
            fig.add_hrect(
                y0=(i - 0.5),
                y1=(i + 0.5),
                layer="below",
                fillcolor="#EBEBEB",
                line_width=0,
                row=2,
                col=2,
            )

    # Add light grey scatter plot (lower right)
    fig.add_trace(
        go.Scatter(
            x=sorted_combo_names * len(sorted_query_names),
            y=[query for query in sorted_query_names for _ in sorted_combo_names],
            mode="markers",
            marker=dict(
                line_width=0,
                color="#CCCCCC",
                line_color="#CCCCCC",
                symbol="circle",
                size=15,
            ),
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    # Add black scatter plot for intersecting combinations (lower right)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(
                line_width=0,
                color="#000000",
                line_color="#000000",
                symbol="circle",
                size=15,
            ),
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    fig.update_layout(
        # height=800, width=1000,
        uniformtext_minsize=12,
        uniformtext_mode="show",
        barmode="group",
        bargap=0.2,
        bargroupgap=0.0,
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        hovermode="closest",
        font_color="black",
    )

    # Update axes
    fig.update_xaxes(
        showticklabels=False,
        side="bottom",
        showline=True,
        linecolor="#000000",
        tickcolor="#000000",
        zeroline=False,
        automargin=True,
        row=1,
        col=2,
    )

    fig.update_yaxes(
        showticklabels=True,
        side="left",
        showgrid=True,
        showline=True,
        title="Intersection Size",
        title_standoff=5,
        title_font_color="#000000",
        linecolor="#000000",
        gridcolor="#E0E0E0",
        ticks="outside",
        tickcolor="#000000",
        zeroline=False,
        automargin=True,
        row=1,
        col=2,
    )

    fig.update_xaxes(
        autorange="reversed",
        side="top",
        showgrid=True,
        showline=True,
        showticklabels=False,
        title="Set Size",
        title_standoff=5,
        title_font_color="#000000",
        gridcolor="#E0E0E0",
        linecolor="#000000",
        ticks="outside",
        tickcolor="#000000",
        tickangle=-90,
        zeroline=False,
        automargin=True,
        row=2,
        col=1,
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=sorted_combo_names,
        side="bottom",
        showline=True,
        showgrid=False,
        showticklabels=False,
        title_standoff=5,
        dtick=1,
        zeroline=False,
        automargin=True,
        row=2,
        col=2,
    )

    fig.update_yaxes(
        type="category",
        categoryorder="array",
        categoryarray=sorted_query_names,
        side="left",
        showline=True,
        showgrid=False,
        showticklabels=True,
        linecolor="#000000",
        ticks="outside",
        tickvals=np.arange(0, len(sorted_query_names)),
        ticktext=[label[:15] for label in sorted_query_names],  # Limit label length
        tickfont=dict(size=10),
        tickcolor="#000000",
        zeroline=False,
        automargin=True,
        row=2,
        col=2,
        tickangle=-45,
    )

    return fig


def calculate_targets_per_query(df):
    df_deduplicated = df.drop_duplicates(subset=["target_name", "query_name"])
    targets_per_query = df_deduplicated.groupby("query_name")["target_name"].nunique()
    result_dict = targets_per_query.to_dict()
    return result_dict


def calculate_intersection_set_counts(df):
    target_query_groups = (
        df.drop_duplicates(subset=["target_name", "query_name"])  # remove duplicates per query
        .groupby("target_name")["query_name"]
        .agg(set)
    )
    query_combinations = target_query_groups.value_counts()
    result_dict = {", ".join(sorted(queries)): int(count) for queries, count in query_combinations.items()}
    return result_dict
