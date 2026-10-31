"""Filtros, indicadores, gráficos e paginação do CP5."""

import math

from dash import Input, Output, ctx, html

from .analytics import dispersao_diaria, intervalo_confianca_media_diaria, kpis, moeda, percentual
from . import charts
from .data import filter_data, filter_options, load_provenance, trace_records
from .layout import GRAPHS
from ..theme import LAYOUT_CLEAN


def filter_inputs():
    return [
        Input("cp5-area", "value"), Input("cp5-years", "value"),
        Input("cp5-dates", "start_date"), Input("cp5-dates", "end_date"),
        Input("cp5-locations", "value"), Input("cp5-subfunctions", "value"),
        Input("cp5-programs", "value"), Input("cp5-units", "value"),
    ]


def _statistic(label, value):
    return html.Div([html.Span(label), html.Strong(value)], className="cp5-statistic")


def _style_figure(figure):
    # As alturas pertencem aos contêineres, como no dashboard principal.
    figure.update_layout(**LAYOUT_CLEAN, height=None, width=None, autosize=True)
    figure.update_layout(
        title=None, margin=dict(l=38, r=18, t=32, b=48),
        legend=dict(orientation="h", y=1.03, yanchor="bottom", x=1, xanchor="right"),
    )
    return figure


def register_cp5_callbacks(app):
    @app.callback(
        [Output(component, "options") for component in ("cp5-locations", "cp5-subfunctions", "cp5-programs", "cp5-units")]
        + [Output(component, "value") for component in ("cp5-locations", "cp5-subfunctions", "cp5-programs", "cp5-units")],
        Input("cp5-area", "value"), Input("cp5-reset", "n_clicks"),
    )
    def update_options(area, _clicks):
        return (*filter_options(area), [], [], [], [])

    @app.callback(
        Output("cp5-area", "value"), Output("cp5-years", "value"),
        Output("cp5-dates", "start_date"), Output("cp5-dates", "end_date"),
        Input("cp5-reset", "n_clicks"), prevent_initial_call=True,
    )
    def reset_filters(_clicks):
        meta = load_provenance()["metadata"]
        return "ALL", meta["anos"], meta["data_minima"], meta["data_maxima"]

    @app.callback(
        [Output(f"cp5-kpi-{key}", "children") for key in ("empenho", "liquidado", "pago", "rap")]
        + [Output(f"cp5-graph-{key}", "figure") for key in GRAPHS]
        + [Output("cp5-statistics", "children"), Output("cp5-record-count", "children")],
        filter_inputs(),
    )
    def update_dashboard(*filters):
        data = filter_data(*filters)
        totals = kpis(data)
        ci = intervalo_confianca_media_diaria(data)
        dispersion = dispersao_diaria(data)
        pearson_figure, pearson = charts.pearson_scatter(data)
        figures = (
            charts.evolucao(data), charts.por_regiao(data), charts.programas(data),
            charts.execucao_subfuncao(data), charts.boxplot_regiao(data),
            charts.histograma(data), charts.corrplot(data), pearson_figure,
        )
        ci_text = (
            f"{moeda(ci['inferior'])} a {moeda(ci['superior'])}"
            if ci["n"] >= 2 else "Dias insuficientes para estimar"
        )
        pearson_text = (
            f"r = {pearson['r']:.3f} · p = {pearson['p']:.3g}"
            if pearson["n"] >= 3 and math.isfinite(pearson["r"]) else "Observações insuficientes"
        )
        statistics = [
            _statistic("IC 95% da média diária paga", ci_text),
            _statistic("Mediana diária", moeda(dispersion["mediana"]) if math.isfinite(dispersion["mediana"]) else "—"),
            _statistic("Desvio padrão diário", moeda(dispersion["desvio"]) if math.isfinite(dispersion["desvio"]) else "—"),
            _statistic("Coeficiente de variação", percentual(dispersion["cv"])),
            _statistic("Pearson · empenhado e pago", pearson_text),
        ]
        count = f"{len(data):,}".replace(",", ".")
        return (
            *[moeda(totals[key]) for key in ("empenho", "liquidado", "pago", "rap")],
            *[_style_figure(figure) for figure in figures],
            statistics, f"{count} registros na seleção",
        )

    @app.callback(
        Output("cp5-records", "data"), Output("cp5-records", "page_count"),
        Output("cp5-records", "page_current"),
        [*filter_inputs(), Input("cp5-records", "page_current"),
         Input("cp5-records", "page_size"), Input("cp5-records", "sort_by")],
    )
    def update_records(*args):
        data = filter_data(*args[:8])
        page, size, sort_by = args[8:]
        size = max(1, min(int(size or 15), 100))
        page_count = max(1, math.ceil(len(data) / size))
        if ctx.triggered_id != "cp5-records":
            page = 0
        page = max(0, min(int(page or 0), page_count - 1))
        return trace_records(data, page, size, sort_by), page_count, page
