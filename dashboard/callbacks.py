"""Interações de navegação e atualização dos gráficos."""

import dash
from dash import ALL, Input, Output, State, html
from dash.exceptions import PreventUpdate

from .config import ANALYSIS_ITEMS, DEFAULT_SECTION, NAV_ITEMS
from .data import select_dataset
from .interpretations import analysis_body
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
        Output("analysis-modal-body", "children"),
        Input({"type": "open-analysis", "chart": ALL}, "n_clicks"),
        State("socio-selection", "data"),
        prevent_initial_call=True,
    )
    def open_analysis(clicks, selection):
        triggered = dash.ctx.triggered_id
        if not any(clicks) or not isinstance(triggered, dict):
            raise PreventUpdate
        chart = triggered.get("chart")
        if not isinstance(chart, str) or chart not in analysis_titles:
            raise PreventUpdate
        body = []
        if chart in CARD_TITLES:
            params = selection or {"outliers": ["iqr"], "confidence": "off"}
            selected, removed, before = select_dataset(data, **params)
            body = analysis_body(chart, data, selected, params.get("confidence") or "off", removed, before)
        return True, f"Análise de dados · {analysis_titles[chart]}", body

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
        content = section() if callable(section) else section
        return html.Div(content, key=active_section, className="section-transition")

