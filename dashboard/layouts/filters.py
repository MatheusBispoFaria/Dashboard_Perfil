"""Controles de filtragem da análise de dados."""

from dash import dcc, html


def _dropdown(label, component_id, values, placeholder):
    return html.Div(className="filter-field", children=[
        html.Label(label, htmlFor=component_id, className="filter-label"),
        dcc.Dropdown(
            id=component_id,
            options=[{"label": value, "value": value} for value in values],
            multi=True,
            placeholder=placeholder,
        ),
    ])


def _range(label, component_id, series, suffix):
    lower, upper = int(series.min()), int(series.max())
    return html.Div(className="filter-field filter-range", children=[
        html.Div(className="range-label-row", children=[
            html.Label(label, htmlFor=component_id, className="filter-label"),
            html.Span(f"{lower}–{upper} {suffix}", className="range-bounds"),
        ]),
        dcc.RangeSlider(
            id=component_id,
            min=lower, max=upper, value=[lower, upper],
            marks=None,
            tooltip={"placement": "bottom", "always_visible": False},
            allowCross=False,
        ),
    ])


def create_filters(data):
    return html.Section(className="filters-panel", **{"aria-label": "Filtros dos dados"}, children=[
        html.Div(className="filters-heading", children=[
            html.Span(className="filters-title", children=[
                html.I(className="fa-solid fa-sliders"), "Refinar dados",
            ]),
            html.Button(
                [html.I(className="fa-solid fa-arrow-rotate-left"), "Limpar filtros"],
                id="btn-reset-filters", n_clicks=0, type="button", className="reset-filters",
            ),
        ]),
        html.Div(className="filters-grid", children=[
            _dropdown("Renda", "filtro-renda", data["income"].unique(), "Todas as rendas"),
            _dropdown(
                "Vínculo", "filtro-vinculo",
                [value for value in data["workclass"].unique() if value != "nan"],
                "Todos os vínculos",
            ),
            _dropdown(
                "Escolaridade", "filtro-escolaridade",
                [value for value in data["education"].unique() if value != "nan"],
                "Todas as formações",
            ),
            _range("Idade", "filtro-idade", data["age"], "anos"),
            _range("Jornada semanal", "filtro-jornada", data["hours_per_week"], "h"),
            html.Div(className="filter-field", children=[
                html.Label("Intervalo de confiança", htmlFor="filtro-ic", className="filter-label"),
                dcc.Dropdown(
                    id="filtro-ic",
                    options=[
                        {"label": "Desativado", "value": "off"},
                        *[{"label": f"{value}%", "value": value} for value in ("90", "95", "99")],
                    ],
                    value="off", clearable=False, searchable=False,
                ),
            ]),
        ]),
    ])
