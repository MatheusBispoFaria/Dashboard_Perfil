"""Visão geral do dashboard e resumo de escolaridade."""

from dash import html

from ..statistics import proportion_interval
from ..theme import C_BLUE, C_CYAN, C_NAVY
from .cards import create_chart_card
from .filters import create_filters


def create_analysis_layout(data):
    return html.Div(className="analysis-page", children=[
        html.Div(className="page-heading", children=[
            html.Div([
                html.P("CENSUS INCOME · ANÁLISE DE DADOS", className="page-eyebrow"),
                html.H1("Renda e perfil socioeconômico", className="header-title"),
                html.P(
                    "Explore as relações entre renda, escolaridade, idade e ocupação.",
                    className="analysis-intro",
                ),
            ]),
            html.Div(className="heading-meta", children=[
                html.Span("Visão geral", className="overview-pill"),
                html.Span(id="selection-summary", className="selection-summary", **{"aria-live": "polite"}),
            ]),
        ]),
        create_filters(data),
        html.Div(className="overview-grid", children=[
            create_chart_card(
                "graph-velocimetro", "INDICADOR GLOBAL", "Participação da renda acima de 50K",
                "fa-arrow-trend-up", "accent-dark",
            ),
            create_chart_card(
                "graph-renda", "COMPOSIÇÃO", "Participação de cada faixa de renda",
                "fa-chart-pie", "accent-mint",
            ),
            create_chart_card(
                "graph-genero", "PERFIL DA BASE", "Distribuição dos registros por gênero",
                "fa-venus-mars", "accent-lilac",
            ),
            create_chart_card(
                "top-escolaridade-container", "FORMAÇÃO", "As três maiores taxas de renda alta",
                "fa-graduation-cap", "education-card",
            ),
        ]),
        html.Div(className="detail-grid", children=[
            create_chart_card(
                "graph-ocupacoes", "MERCADO DE TRABALHO", "As dez ocupações mais frequentes na seleção",
                "fa-briefcase", "occupation-card",
            ),
            create_chart_card(
                "graph-idade-renda", "DISTRIBUIÇÃO ETÁRIA", "Quantidade de pessoas por idade e faixa de renda",
                "fa-chart-area", "age-card",
            ),
        ]),
        html.Div(className="journey-grid", children=[
            create_chart_card(
                "graph-horas-idade", "JORNADA SEMANAL", "Média de horas de trabalho por idade",
                "fa-clock", "hours-card",
            ),
            create_chart_card(
                "graph-donut-homens", "RENDA POR GÊNERO", "Taxa de renda acima de 50K no grupo masculino",
                "fa-mars", "gender-income-card",
            ),
            create_chart_card(
                "graph-donut-mulheres", "RENDA POR GÊNERO", "Taxa de renda acima de 50K no grupo feminino",
                "fa-venus", "gender-income-card",
            ),
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
                    className="education-label",
                    style={
                        "color": colors[index],
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
