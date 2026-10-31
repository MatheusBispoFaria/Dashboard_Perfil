"""Interface do dashboard de despesas públicas do CP5."""

from dash import dash_table, dcc, html

from .data import AREAS, TRACE_COLUMNS, load_provenance
from ..layouts.projects import page_heading

GRAPHS = {
    "evolution": ("Evolução financeira", "Empenhado, liquidado e pago ao longo do tempo"),
    "region": ("Localizador territorial", "Valores pagos por localizador da fonte oficial"),
    "program": ("Principais programas", "Os oito programas com maiores valores pagos"),
    "subfunction": ("Estágios por subfunção", "Comparação dos movimentos financeiros"),
    "box": ("Dispersão dos pagamentos", "Valores pagos por dia e localizador territorial"),
    "hist": ("Distribuição dos pagamentos", "Valores por registro, excluindo pagamentos iguais a zero"),
    "corr": ("Correlação diária", "Relação entre as quatro medidas financeiras"),
    "pearson": ("Empenhado × pago", "Correlação de Pearson sobre os totais diários"),
}


def _field(label, component):
    return html.Div(className="filter-field", children=[
        html.Label(label, className="filter-label"), component,
    ])


def _multi(component_id):
    return dcc.Dropdown(id=component_id, options=[], multi=True, placeholder="Todos")


def _graph_card(key, title, subtitle):
    return html.Article(className="chart-card", children=[
        html.Div(className="chart-card-heading", children=[
            html.Span("CP5 · DATA SCIENCE", className="card-eyebrow"),
            html.Button(
                "↗", id={"type": "open-analysis", "chart": f"cp5-{key}"},
                className="chart-expand", n_clicks=0, type="button",
                **{"aria-label": f"Abrir análise: {title}", "aria-haspopup": "dialog"},
            ),
        ]),
        html.H2(title, className="chart-title"),
        html.P(subtitle, className="chart-subtitle"),
        html.Div(className="cp5-graph", children=dcc.Graph(
            id=f"cp5-graph-{key}", responsive=True,
            style={"width": "100%", "height": "100%"},
            config={"displayModeBar": False, "responsive": True},
        )),
    ])


def create_cp5_layout():
    provenance = load_provenance()
    meta = provenance["metadata"]
    start, end = meta["data_minima"], meta["data_maxima"]
    audit = provenance["auditoria"]
    return html.Div(className="cp5-page", children=[
        page_heading(
            "CP5 · DATA SCIENCE · 2024–2025", "Despesas públicas do Espírito Santo",
            "Despesas públicas do Espírito Santo em 2024 e 2025: explore os dados, compare áreas e acompanhe os movimentos financeiros.",
        ),
        html.Section(className="filters-panel", children=[
            html.Div(className="filters-heading", children=[
                html.Span("Explorar despesas", className="filters-title"),
                html.Button("Limpar filtros", id="cp5-reset", n_clicks=0, type="button", className="reset-filters"),
            ]),
            html.Div(className="cp5-filters-grid", children=[
                _field("Área", dcc.Dropdown(
                    id="cp5-area", options=[{"label": "Todas as áreas", "value": "ALL"}]
                    + [{"label": area.title(), "value": area} for area in AREAS],
                    value="ALL", clearable=False,
                )),
                _field("Ano", dcc.Dropdown(
                    id="cp5-years", options=[{"label": str(year), "value": year} for year in meta["anos"]],
                    value=meta["anos"], multi=True,
                )),
                _field("Período", dcc.DatePickerRange(
                    id="cp5-dates", min_date_allowed=start, max_date_allowed=end,
                    start_date=start, end_date=end, display_format="DD/MM/YYYY",
                    first_day_of_week=1,
                )),
                _field("Localizador territorial", _multi("cp5-locations")),
                _field("Subfunção", _multi("cp5-subfunctions")),
                _field("Programa", _multi("cp5-programs")),
                _field("Unidade gestora", _multi("cp5-units")),
            ]),
        ]),
        dcc.Loading(type="circle", color="#626bff", children=html.Div([
            html.Div(className="cp5-kpi-grid", children=[
                html.Div(className="cp5-kpi", children=[
                    html.Span(label, className="cp5-kpi-label"),
                    html.Strong("—", id=f"cp5-kpi-{key}"),
                ])
                for key, label in (
                    ("empenho", "Empenhado"), ("liquidado", "Liquidado"),
                    ("pago", "Pago"), ("rap", "Restos a pagar"),
                )
            ]),
            html.P(id="cp5-record-count", className="cp5-selection", **{"aria-live": "polite"}),
            html.P(
                "Os valores representam movimentos registrados na fonte e podem incluir ajustes negativos. "
                "Pago e empenhado são apresentados separadamente.", className="cp5-method-note",
            ),
            html.Div(className="cp5-charts-grid", children=[
                _graph_card(key, *labels) for key, labels in GRAPHS.items()
            ]),
            html.Section(className="project-card", children=[
                html.H2("Leitura estatística", className="project-title"),
                html.Div(id="cp5-statistics", className="cp5-statistics"),
            ]),
        ])),
        html.Details(className="cp5-details", children=[
            html.Summary("Ver registros do recorte"),
            dash_table.DataTable(
                id="cp5-records", columns=[{"name": column, "id": column} for column in TRACE_COLUMNS],
                data=[], page_current=0, page_size=15, page_action="custom",
                sort_action="custom", sort_mode="multi", sort_by=[],
                style_table={"overflowX": "auto"},
                style_cell={"fontFamily": "Segoe UI, sans-serif", "fontSize": 11, "textAlign": "left", "padding": "10px", "minWidth": "100px", "maxWidth": "280px", "whiteSpace": "normal"},
                style_header={"backgroundColor": "#eff1f8", "fontWeight": "600"},
            ),
        ]),
        html.Details(className="cp5-details", children=[
            html.Summary("Origem e preparação dos dados"),
            html.P(
                f"Base integral: {meta['registros_base_integral']:,} registros. "
                f"Recorte das cinco áreas: {meta['registros_recorte']:,} registros. "
                "Foram utilizadas as oito partes de 2024 e 2025 fornecidas no projeto, sem amostragem do recorte."
                .replace(",", "."),
            ),
            html.P(provenance["tratamento"]),
            html.P(
                f"Auditoria da base integral: {audit['duplicados_id_base_integral']} duplicidades por ID e "
                f"{audit['datas_invalidas_base_integral']} datas inválidas. "
                "O histórico de preparação foi preservado junto ao conjunto de dados."
            ),
        ]),
    ])
