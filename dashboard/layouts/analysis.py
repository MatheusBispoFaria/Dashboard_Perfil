"""Tela da análise de dados e resumo de escolaridade."""

from dash import dcc, html
import dash_bootstrap_components as dbc

from ..statistics import proportion_interval
from ..theme import C_BLUE, C_CYAN, C_NAVY
from .filters import create_filters


def _chart_column(width, title, graph_id):
    return dbc.Col(width=width, children=[
        html.Div(className="dash-card", children=[
            html.Div(title, className="card-title-sm"),
            dcc.Graph(id=graph_id, config={"displayModeBar": False}),
        ]),
    ])


def _gender_income_column(title, description, graph_id):
    return dbc.Col(width=4, children=[
        html.Div(
            className="dash-card d-flex flex-row align-items-center",
            children=[
                html.Div(style={"width": "100px"}, children=[
                    dcc.Graph(id=graph_id, config={"displayModeBar": False}),
                ]),
                html.Div(className="ms-3", children=[
                    html.Div(
                        title, className="card-title-sm",
                        style={"border": "none", "margin": 0, "padding": 0},
                    ),
                    html.P(
                        description,
                        style={"fontSize": "12px", "color": "#64748b", "margin": 0},
                    ),
                ]),
            ],
        ),
    ])


def create_analysis_layout(data):
    return html.Div([
        create_filters(data),
        dbc.Row(className="mb-4", children=[
            _chart_column(6, "DISTRIBUIÇÃO DE OCUPAÇÕES", "graph-ocupacoes"),
            _chart_column(3, "DISTRIBUIÇÃO DE RENDA", "graph-renda"),
            _chart_column(3, "GÊNERO NA BASE", "graph-genero"),
        ]),
        dbc.Row(className="mb-4", children=[
            _chart_column(4, "DENSIDADE DE IDADE POR RENDA", "graph-idade-renda"),
            _chart_column(4, "MÉDIA DE HORAS/SEMANA POR IDADE", "graph-horas-idade"),
            _chart_column(4, "% RENDA ALTA GLOBAL (>50K)", "graph-velocimetro"),
        ]),
        dbc.Row(children=[
            _gender_income_column(
                "HOMENS (>50K)", "Taxa de alta renda no grupo masculino",
                "graph-donut-homens",
            ),
            _gender_income_column(
                "MULHERES (>50K)", "Taxa de alta renda no grupo feminino",
                "graph-donut-mulheres",
            ),
            dbc.Col(width=4, children=[
                html.Div(className="dash-card justify-content-center", children=[
                    html.Div("TOP ESCOLARIDADE (>50K)", className="card-title-sm mb-3"),
                    html.Div(id="top-escolaridade-container")
                ])
            ]),
        ]),
    ])


def create_education_summary(data, confidence="off"):
    top_education = (
        data.groupby("education")["renda_alta"]
        .mean().sort_values(ascending=False).head(3) * 100
    )
    colors = [C_CYAN, C_BLUE, C_NAVY]
    summary = []
    for index, (education, percentage) in enumerate(top_education.items()):
        value = f"{percentage:.1f}%"
        if confidence != "off":
            group = data[data["education"] == education]
            lower, upper = proportion_interval(
                group["renda_alta"].sum(), len(group), confidence
            )
            value = html.Div([
                html.Span(f"{percentage:.1f}%"),
                html.Br(),
                html.Small(
                    f"IC {confidence}%: {lower:.1f}–{upper:.1f}%",
                    style={"fontWeight": "normal"},
                ),
            ], className="text-end")

        summary.append(
            html.Div([
                html.Div(
                    className="d-flex justify-content-between mb-1",
                    style={
                        "fontSize": "11px", "fontWeight": "bold", "color": colors[index],
                    },
                    children=[html.Span(education), value],
                ),
                html.Div(className="progress-bar-container", children=[
                    html.Div(className="progress-track", children=[
                        html.Div(className="progress-fill", style={
                            "width": f"{percentage}%", "backgroundColor": colors[index],
                        }),
                    ]),
                ]),
            ])
        )
    return summary
