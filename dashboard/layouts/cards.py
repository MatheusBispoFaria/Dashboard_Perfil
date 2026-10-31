"""Cartões compartilhados e acesso à futura análise detalhada."""

from dash import dcc, html

CARD_TITLES = {
    "graph-velocimetro": "Renda alta global",
    "graph-renda": "Distribuição de renda",
    "graph-genero": "Gênero na base",
    "top-escolaridade-container": "Escolaridade e renda",
    "graph-ocupacoes": "Distribuição de ocupações",
    "graph-idade-renda": "Idade por faixa de renda",
    "graph-horas-idade": "Jornada ao longo da idade",
    "graph-donut-homens": "Renda alta · Homens",
    "graph-donut-mulheres": "Renda alta · Mulheres",
}


def create_chart_card(component_id, eyebrow, subtitle, icon, class_name=""):
    """Todos os gráficos oferecem o mesmo botão acessível de análise."""
    title = CARD_TITLES[component_id]
    if component_id == "top-escolaridade-container":
        content = html.Div(id=component_id, className="education-summary")
    else:
        # A altura fica no contêiner, pois o modo responsivo do Dash aplica
        # height: 100% ao Graph e precisa de um pai com altura definida.
        content = html.Div(
            className="card-graph",
            children=dcc.Graph(
                id=component_id,
                responsive=True,
                config={"displayModeBar": False, "responsive": True},
                style={"width": "100%", "height": "100%"},
            ),
        )
    return html.Article(className=f"chart-card {class_name}".strip(), children=[
        html.Div(className="chart-card-heading", children=[
            html.Span(className="card-icon", children=html.I(className=f"fa-solid {icon}")),
            html.Span(eyebrow, className="card-eyebrow"),
            html.Button(
                "↗",
                id={"type": "open-analysis", "chart": component_id},
                className="chart-expand",
                n_clicks=0,
                type="button",
                title=f"Abrir análise: {title}",
                **{"aria-label": f"Abrir análise: {title}", "aria-haspopup": "dialog"},
            ),
        ]),
        html.H2(title, className="chart-title"),
        html.P(subtitle, className="chart-subtitle"),
        content,
    ])
