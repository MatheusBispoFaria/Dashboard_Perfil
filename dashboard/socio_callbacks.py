"""Interações da análise socioeconômica, com um único recorte coerente."""

import math

from dash import Input, Output, State, ctx, dcc
from dash.exceptions import PreventUpdate

from .charts import create_dashboard_figures
from .data import select_dataset
from .labels import integer
from .layouts.cards import CARD_TITLES
from .socioeconomic import TABLE_COLUMNS, query_records

FILTERS = (
    ("filtro-renda", "income"), ("filtro-vinculo", "workclass"),
    ("filtro-escolaridade", "education"), ("filtro-idade", "age"),
    ("filtro-jornada", "hours"), ("filtro-genero", "sex"),
    ("filtro-extremos", "outliers"), ("filtro-ic", "confidence"),
)


def filter_inputs():
    return [Input(component, "value") for component, _ in FILTERS]


def selection_params(values):
    return {name: value for (_, name), value in zip(FILTERS, values)}


def register_socio_callbacks(app, data):
    @app.callback(
        [Output(component, "value") for component, _ in FILTERS],
        Input("btn-reset-filters", "n_clicks"), prevent_initial_call=True,
    )
    def reset_filters(_clicks):
        return ([], [], [], [int(data["age"].min()), int(data["age"].max())],
                [int(data["hours_per_week"].min()), int(data["hours_per_week"].max())],
                [], ["iqr"], "off")

    @app.callback(
        [Output(chart, "figure") for chart in CARD_TITLES]
        + [Output("selection-summary", "children"), Output("socio-filter-note", "children"),
           Output("socio-selection", "data")],
        filter_inputs(),
    )
    def update_dashboard(*values):
        params = selection_params(values)
        selected, removed, before = select_dataset(data, **params)
        figures = create_dashboard_figures(selected, params.get("confidence") or "off")
        if "iqr" in (params.get("outliers") or []):
            note = (f"IQR ativado: {integer(removed)} de {integer(before)} registros excluídos por idade ou jornada. "
                    f"Os {integer(len(selected))} restantes alimentam todos os gráficos e a consulta da base. "
                    "Limites fixos: idade até 78 anos; jornada de 32,5 a 52,5 h/semana. Extremos podem ser observações legítimas.")
        else:
            note = f"IQR desativado: nenhum registro foi excluído por essa regra. {integer(len(selected))} registros atendem aos filtros atuais."
        return (*[figures[chart] for chart in CARD_TITLES],
                f"{integer(len(selected))} registros na seleção", note, params)

    @app.callback(
        Output("socio-records", "data"), Output("socio-records", "page_count"),
        Output("socio-records", "page_current"), Output("socio-record-summary", "children"),
        [*filter_inputs(), Input("socio-search", "value"), Input("socio-records", "page_current"),
         Input("socio-records", "page_size"), Input("socio-records", "sort_by")],
    )
    def update_records(*values):
        params = selection_params(values[:len(FILTERS)])
        search, page, size, sort_by = values[len(FILTERS):]
        selected, _, _ = select_dataset(data, **params)
        records = query_records(selected, search, sort_by)
        size = max(1, min(int(size or 15), 100))
        pages = max(1, math.ceil(len(records)/size))
        changed = ctx.triggered[0]["prop_id"] if ctx.triggered else ""
        page = int(page or 0) if changed.endswith(".page_current") else 0
        page = max(0, min(page, pages-1))
        visible = records.iloc[page*size:(page+1)*size]
        return (visible.where(visible.notna(), None).to_dict("records"), pages, page,
                f"{integer(len(records))} registros na consulta · {integer(len(selected))} na seleção dos gráficos · página {page+1} de {pages}")

    @app.callback(
        Output("socio-download", "data"), Input("socio-export", "n_clicks"),
        [*[State(component, "value") for component, _ in FILTERS],
         State("socio-search", "value"), State("socio-records", "sort_by")],
        prevent_initial_call=True,
    )
    def export_records(clicks, *values):
        if not clicks:
            raise PreventUpdate
        selected, _, _ = select_dataset(data, **selection_params(values[:len(FILTERS)]))
        search, sort_by = values[len(FILTERS):]
        records = query_records(selected, search, sort_by).rename(columns=TABLE_COLUMNS)
        content = "\ufeff" + records.to_csv(index=False, sep=";")
        return dcc.send_string(content, "adult-selecao-socioeconomica.csv", type="text/csv;charset=utf-8")
