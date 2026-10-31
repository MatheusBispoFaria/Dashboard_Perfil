"""Construção dos oito gráficos do dashboard, sem dependência dos callbacks."""

import plotly.express as px
import plotly.graph_objects as go

from .statistics import CONFIDENCE_Z, proportion_interval
from .theme import C_BLUE, C_CYAN, C_LIGHT_BLUE, C_NAVY, LAYOUT_CLEAN


def create_occupation_figure(data):
    occ_counts = (
        data[data["occupation"] != "nan"]["occupation"]
        .value_counts().head(10).reset_index()
    )
    fig_bar = px.bar(
        occ_counts, x="occupation", y="count", color_discrete_sequence=[C_NAVY]
    )
    fig_bar.update_layout(**LAYOUT_CLEAN, height=238)
    fig_bar.update_traces(marker_line_width=0, hovertemplate="%{x}: <b>%{y}</b>")
    fig_bar.update_xaxes(title="", tickangle=-35)
    fig_bar.update_yaxes(title="")
    return fig_bar


def create_income_figure(data):
    income_counts = data["income"].value_counts().reset_index()
    fig_pie = px.pie(
        income_counts, values="count", names="income", color="income", hole=0,
        color_discrete_map={"<=50K": C_BLUE, ">50K": C_CYAN},
    )
    fig_pie.update_layout(
        **LAYOUT_CLEAN, height=178, showlegend=True,
        legend=dict(orientation="h", y=-0.02, x=0.5, xanchor="center", font_size=9),
    )
    fig_pie.update_traces(textinfo="percent", textfont_size=10, marker_line_width=0)
    return fig_pie


def create_gender_figure(data):
    sex_counts = data["sex"].value_counts().reset_index()
    fig_donut = px.pie(
        sex_counts, values="count", names="sex", color="sex", hole=0.72,
        color_discrete_map={"Male": C_NAVY, "Female": C_LIGHT_BLUE},
    )
    fig_donut.update_layout(
        **LAYOUT_CLEAN, height=178, showlegend=True,
        legend=dict(orientation="h", y=-0.02, x=0.5, xanchor="center", font_size=9),
    )
    fig_donut.add_annotation(
        text="GÊNERO", x=0.5, y=0.5, font_size=10,
        font_weight="normal", showarrow=False, font_color="#64748b",
    )
    fig_donut.update_traces(textinfo="percent", textposition="inside", textfont_size=10)
    return fig_donut


def create_age_income_figure(data):
    age_income = data.groupby(["age", "income"]).size().reset_index(name="count")
    fig_area = px.area(
        age_income, x="age", y="count", color="income",
        color_discrete_map={"<=50K": C_LIGHT_BLUE, ">50K": C_NAVY},
    )
    fig_area.update_layout(**LAYOUT_CLEAN, height=238, showlegend=False)
    fig_area.update_xaxes(title="", showgrid=False)
    fig_area.update_yaxes(title="")
    return fig_area


def create_hours_age_figure(data, confidence="off"):
    if confidence != "off":
        hours_age = (
            data.groupby("age")["hours_per_week"]
            .agg(["mean", "std", "count"]).reset_index()
        )
        hours_age["std"] = hours_age["std"].fillna(0)
        hours_age["erro_ic"] = (
            CONFIDENCE_Z[confidence] * hours_age["std"] / hours_age["count"].pow(0.5)
        )
        fig_line = px.line(hours_age, x="age", y="mean", markers=True, error_y="erro_ic")
    else:
        hours_age = data.groupby("age")["hours_per_week"].mean().reset_index()
        fig_line = px.line(hours_age, x="age", y="hours_per_week", markers=True)
    fig_line.update_traces(line_color=C_BLUE, marker=dict(size=4, color=C_CYAN))
    fig_line.update_layout(**LAYOUT_CLEAN, height=200, showlegend=False)
    fig_line.update_xaxes(title="", showgrid=False)
    fig_line.update_yaxes(title="")
    return fig_line


def create_income_gauge(data, confidence="off"):
    pct_alta = data["renda_alta"].mean() * 100
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_alta,
        number={
            "suffix": "%", "valueformat": ".1f",
            "font": {"size": 30, "color": "#ffffff", "weight": "normal"},
        },
        gauge={
            "axis": {"range": [0, 100], "visible": False},
            "bar": {"color": C_CYAN, "thickness": 0.75},
            "bgcolor": "#e2e8f0",
            "steps": [
                {"range": [0, 50], "color": "#485256"},
                {"range": [50, 100], "color": "#373e42"},
            ],
        },
    ))
    fig_gauge.update_layout(**LAYOUT_CLEAN, height=178)
    if confidence != "off":
        lower, upper = proportion_interval(
            data["renda_alta"].sum(), len(data), confidence
        )
        fig_gauge.add_annotation(
            text=f"IC {confidence}%: {lower:.1f}% – {upper:.1f}%",
            x=0.5, y=0.02, showarrow=False, font_size=9, font_color="#cfdddd",
        )
    return fig_gauge


def create_gender_income_figure(data, sex, color, confidence="off"):
    group_data = data[data["sex"] == sex]
    percentage = group_data["renda_alta"].mean() * 100 if not group_data.empty else 0
    figure = go.Figure(go.Pie(
        values=[percentage, 100 - percentage], hole=0.75,
        marker_colors=[color, "#e2e8f0"],
    ))
    figure.update_layout(**LAYOUT_CLEAN, height=200, showlegend=False)
    figure.update_traces(textinfo="none", hovertemplate="%{value:.1f}%<extra></extra>")
    label = f"{percentage:.1f}%"
    if confidence != "off" and not group_data.empty:
        lower, upper = proportion_interval(
            group_data["renda_alta"].sum(), len(group_data), confidence
        )
        label += (
            f"<br><span style='font-size:8px'>"
            f"IC {confidence}%: {lower:.1f}–{upper:.1f}%</span>"
        )
    figure.add_annotation(
        text=label, x=0.5, y=0.5, font_size=24,
        font_weight="normal", showarrow=False, font_color=color,
    )
    return figure


def create_dashboard_figures(data, confidence="off"):
    """Retorna os gráficos na ordem esperada pelos componentes da tela."""
    if data.empty:
        return tuple(go.Figure().update_layout(**LAYOUT_CLEAN) for _ in range(8))

    return (
        create_occupation_figure(data),
        create_income_figure(data),
        create_gender_figure(data),
        create_age_income_figure(data),
        create_hours_age_figure(data, confidence),
        create_income_gauge(data, confidence),
        create_gender_income_figure(data, "Male", C_CYAN, confidence),
        create_gender_income_figure(data, "Female", C_BLUE, confidence),
    )
