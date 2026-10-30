"""Interações de navegação e atualização dos gráficos."""

import dash
from dash import Input, Output, State, html

from .charts import create_dashboard_figures
from .config import DEFAULT_SECTION, NAV_ITEMS
from .data import filter_dataset
from .layouts.analysis import create_education_summary


def register_callbacks(app, data, sections):
    """Registra as interações para a instância recebida."""

    @app.callback(
        Output("sidebar", "className"),
        Input("btn-toggle-sidebar", "n_clicks"),
        State("sidebar", "className"),
        prevent_initial_call=True,
    )
    def toggle_sidebar(_n_clicks, current_class):
        return "sidebar" if "collapsed" in current_class else "sidebar collapsed"

    @app.callback(
        [Output("active-section", "data")]
        + [Output(f"nav-{section}", "className") for section, _, _ in NAV_ITEMS],
        [Input(f"nav-{section}", "n_clicks") for section, _, _ in NAV_ITEMS],
        State("active-section", "data"),
    )
    def update_active_section(*args):
        current_section = args[-1]
        context = dash.callback_context
        if not context.triggered:
            active_section = DEFAULT_SECTION
        else:
            button_id = context.triggered[0]["prop_id"].split(".")[0]
            active_section = next(
                (section for section, _, _ in NAV_ITEMS if button_id == f"nav-{section}"),
                None,
            )
            if active_section is None:
                return (current_section, *["nav-item" for _ in NAV_ITEMS])

        classes = [
            "nav-item active" if section == active_section else "nav-item"
            for section, _, _ in NAV_ITEMS
        ]
        return (active_section, *classes)

    @app.callback(
        Output("tab-content-container", "children"),
        Input("active-section", "data"),
    )
    def render_content(active_section):
        return sections.get(active_section, sections[DEFAULT_SECTION])

    @app.callback(
        [
            Output("graph-ocupacoes", "figure"),
            Output("graph-renda", "figure"),
            Output("graph-genero", "figure"),
            Output("graph-idade-renda", "figure"),
            Output("graph-horas-idade", "figure"),
            Output("graph-velocimetro", "figure"),
            Output("graph-donut-homens", "figure"),
            Output("graph-donut-mulheres", "figure"),
            Output("top-escolaridade-container", "children"),
        ],
        [
            Input("filtro-renda", "value"),
            Input("filtro-vinculo", "value"),
            Input("filtro-escolaridade", "value"),
            Input("filtro-idade", "value"),
            Input("filtro-jornada", "value"),
            Input("filtro-ic", "value"),
        ],
        prevent_initial_call=False,
    )
    def update_dashboard(income, workclass, education, age, hours, confidence):
        filtered = filter_dataset(data, income, workclass, education, age, hours)
        figures = create_dashboard_figures(filtered, confidence)
        if filtered.empty:
            return [*figures, html.Div("Sem dados para esta seleção.")]
        return (*figures, create_education_summary(filtered, confidence))
