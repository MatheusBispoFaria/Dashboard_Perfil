"""Interações de navegação e atualização dos gráficos."""

import dash
from dash import ALL, Input, Output, State, html
from dash.exceptions import PreventUpdate

from .charts import create_dashboard_figures
from .config import ANALYSIS_ITEMS, DEFAULT_SECTION, NAV_ITEMS
from .data import filter_dataset
from .layouts.analysis import create_education_summary
from .layouts.cards import CARD_TITLES
from .cp5.layout import GRAPHS as CP5_GRAPHS


def register_callbacks(app, data, sections):
    """Registra as interações para a instância recebida."""
    analysis_titles = {
        **CARD_TITLES,
        **{f"cp5-{key}": labels[0] for key, labels in CP5_GRAPHS.items()},
    }

    @app.callback(
        Output("top-navigation", "className"),
        Output("btn-toggle-navigation", "aria-expanded"),
        Output("btn-toggle-navigation", "aria-label"),
        Input("btn-toggle-navigation", "n_clicks"),
        Input("nav-inicio", "n_clicks"),
        State("top-navigation", "className"),
        prevent_initial_call=True,
    )
    def toggle_navigation(_n_clicks, _home_clicks, current_class):
        if dash.ctx.triggered_id == "nav-inicio":
            return "top-navigation collapsed", "false", "Abrir navegação"
        if "collapsed" in current_class:
            return "top-navigation", "true", "Recolher navegação"
        return "top-navigation collapsed", "false", "Abrir navegação"

    @app.callback(
        Output("analysis-modal", "is_open"),
        Output("analysis-modal-title", "children"),
        Input({"type": "open-analysis", "chart": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def open_analysis(clicks):
        triggered = dash.ctx.triggered_id
        if not any(clicks) or not isinstance(triggered, dict):
            raise PreventUpdate
        chart = triggered.get("chart")
        if not isinstance(chart, str) or chart not in analysis_titles:
            raise PreventUpdate
        return True, f"Análise de dados · {analysis_titles[chart]}"

    @app.callback(
        Output("filtro-renda", "value"),
        Output("filtro-vinculo", "value"),
        Output("filtro-escolaridade", "value"),
        Output("filtro-idade", "value"),
        Output("filtro-jornada", "value"),
        Output("filtro-ic", "value"),
        Input("btn-reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(_n_clicks):
        return (
            [], [], [],
            [int(data["age"].min()), int(data["age"].max())],
            [int(data["hours_per_week"].min()), int(data["hours_per_week"].max())],
            "off",
        )

    @app.callback(
        [Output("active-section", "data")]
        + [Output(f"nav-{section}", "className") for section, _, _ in NAV_ITEMS],
        [Input(f"nav-{section}", "n_clicks") for section, _, _ in NAV_ITEMS]
        + [Input("nav-inicio", "n_clicks"), Input("analysis-selector", "value")],
        State("active-section", "data"),
    )
    def update_active_section(*args):
        current_section = args[-1]
        selected_analysis = args[len(NAV_ITEMS) + 1]
        analysis_sections = {value for value, _ in ANALYSIS_ITEMS}
        context = dash.callback_context
        if not context.triggered:
            active_section = DEFAULT_SECTION
        else:
            button_id = context.triggered[0]["prop_id"].split(".")[0]
            if button_id == "nav-inicio":
                active_section = DEFAULT_SECTION
            elif button_id == "analysis-selector":
                active_section = selected_analysis if current_section in analysis_sections and selected_analysis in analysis_sections else current_section
            elif button_id == "nav-analise-dados":
                active_section = selected_analysis if selected_analysis in analysis_sections else "analise-dados"
            else:
                active_section = next(
                    (section for section, _, _ in NAV_ITEMS if button_id == f"nav-{section}"),
                    current_section,
                )

        classes = [
            "nav-item active" if section == active_section or (section == "analise-dados" and active_section in analysis_sections) else "nav-item"
            for section, _, _ in NAV_ITEMS
        ]
        return (active_section, *classes)

    @app.callback(Output("portfolio-shell", "className"), Input("active-section", "data"))
    def update_shell(active_section):
        if active_section == DEFAULT_SECTION:
            return "dashboard-wrapper portfolio-shell is-home"
        analysis_class = " section-analysis" if active_section in {value for value, _ in ANALYSIS_ITEMS} else ""
        return f"dashboard-wrapper portfolio-shell is-workspace{analysis_class}"

    @app.callback(
        Output("tab-content-container", "children"),
        Input("active-section", "data"),
    )
    def render_content(active_section):
        section = sections.get(active_section, sections[DEFAULT_SECTION])
        return section() if callable(section) else section

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
            Output("selection-summary", "children"),
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
        count = f"{len(filtered):,}".replace(",", ".")
        summary = f"{count} registros na seleção"
        if filtered.empty:
            return [*figures, html.Div("Sem dados para esta seleção."), summary]
        return (*figures, create_education_summary(filtered, confidence), summary)
