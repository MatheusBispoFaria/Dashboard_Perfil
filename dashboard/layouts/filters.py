"""Filtros compartilhados por todos os gráficos e pela consulta da base."""

from dash import dcc, html
import dash_bootstrap_components as dbc

from ..labels import EDUCATION, EDUCATION_ORDER, INCOME, SEX, WORKCLASS, label


def _dropdown(title, component_id, values, mapping, placeholder):
    return html.Div(className="filter-field", children=[
        html.Label(title, htmlFor=component_id, className="filter-label"),
        dcc.Dropdown(id=component_id, options=[{"label": label(value, mapping), "value": value} for value in values],
                     value=[], multi=True, placeholder=placeholder),
    ])


def _range(title, component_id, series, suffix):
    lower, upper = int(series.min()), int(series.max())
    return html.Div(className="filter-field filter-range", children=[
        html.Div(className="range-label-row", children=[
            html.Label(title, htmlFor=component_id, className="filter-label"),
            html.Span(f"{lower}–{upper} {suffix}", className="range-bounds"),
        ]),
        dcc.RangeSlider(id=component_id, min=lower, max=upper, value=[lower, upper],
                        marks=None, tooltip={"placement": "bottom", "always_visible": False}, allowCross=False),
    ])


def create_filters(data):
    education = [value for value in EDUCATION_ORDER if value in set(data["education"])]
    education += sorted(set(data["education"])-set(education))
    return html.Section(className="filters-panel socio-filters", **{"aria-label": "Filtros dos dados"}, children=[
        html.Div(className="filters-heading", children=[
            html.Span("Refinar dados", className="filters-title"),
            html.Button("Limpar filtros", id="btn-reset-filters", n_clicks=0, type="button", className="reset-filters"),
        ]),
        html.Div(className="socio-filters-grid", children=[
            _dropdown("Renda anual", "filtro-renda", list(INCOME), INCOME, "Todas as faixas"),
            _dropdown("Gênero (sexo na fonte)", "filtro-genero", list(SEX), SEX, "Todos os grupos"),
            _dropdown("Vínculo de trabalho", "filtro-vinculo", data["workclass"].unique(), WORKCLASS, "Todos os vínculos"),
            _dropdown("Escolaridade", "filtro-escolaridade", education, EDUCATION, "Todas as formações"),
            _range("Idade", "filtro-idade", data["age"], "anos"),
            _range("Jornada semanal", "filtro-jornada", data["hours_per_week"], "h"),
            html.Div(className="filter-field", children=[
                html.Label("Intervalo de confiança", htmlFor="filtro-ic", className="filter-label"),
                dcc.Dropdown(id="filtro-ic", options=[{"label": "Não exibir", "value": "off"}]
                             + [{"label": f"{value}%", "value": value} for value in ("90", "95", "99")],
                             value="off", clearable=False, searchable=False),
            ]),
            html.Div(className="filter-field iqr-field", children=[
                html.Div(className="filter-label iqr-label", children=[
                    html.Span("Tratamento de extremos · "),
                    html.Button("IQR", id="socio-iqr-help", type="button", className="iqr-help-link",
                                **{"aria-label": "Como funciona o IQR", "aria-haspopup": "dialog"}),
                ]),
                dcc.Checklist(id="filtro-extremos", options=[{"label": " Ocultar extremos", "value": "iqr"}],
                              value=[], inputClassName="iqr-checkbox"),
                dbc.Popover([
                    dbc.PopoverHeader("IQR · Intervalo interquartil"),
                    dbc.PopoverBody([
                        html.P("O IQR é a diferença entre o terceiro e o primeiro quartil (Q3 − Q1), que delimitam os 50% centrais dos valores."),
                        html.P("A regra de Tukey considera extremos os valores abaixo de Q1 − 1,5 × IQR ou acima de Q3 + 1,5 × IQR."),
                        html.P("Aqui, os limites são calculados na base completa e permanecem fixos: −2 a 78 anos e 32,5 a 52,5 horas semanais. Ao ativar, apenas registros dentro dos dois intervalos entram nos gráficos, na consulta e no CSV."),
                        html.P("O filtro começa desativado. Extremos podem ser legítimos, como jornadas parciais ou extensas; a exclusão serve para comparar recortes, não para corrigir automaticamente a base."),
                    ]),
                ], id="socio-iqr-popover", target="socio-iqr-help", trigger="hover focus",
                    placement="auto", autohide=False, class_name="socio-iqr-popover"),
            ]),
        ]),
        html.P(id="socio-filter-note", className="socio-filter-note", **{"aria-live": "polite"}),
    ])
