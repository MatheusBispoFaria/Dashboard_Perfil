"""Entrada do portfólio, navegação expansível e dashboards preservados."""

from dash import dcc, html
import dash_bootstrap_components as dbc

from ..config import ANALYSIS_ITEMS, DEFAULT_SECTION, NAV_ITEMS


def create_navigation():
    return html.Nav(
        id="top-navigation", className="top-navigation collapsed",
        **{"aria-label": "Navegação principal"},
        children=[
            html.Button([
                html.Span(f"0{index + 1}", className="nav-number", **{"aria-hidden": "true"}),
                html.Span(label, className="nav-label"),
                html.Span("↗", className="nav-arrow", **{"aria-hidden": "true"}),
            ], id=f"nav-{section}", className="nav-item", n_clicks=0, type="button")
            for index, (section, label, _) in enumerate(NAV_ITEMS)
        ],
    )


def create_main_layout(profile_url, artwork_url):
    return html.Div(id="portfolio-shell", className="dashboard-wrapper portfolio-shell is-home", children=[
        dcc.Store(id="active-section", data=DEFAULT_SECTION),
        html.Header(className="portfolio-header", children=[
            html.Img(src=artwork_url, alt="", className="hero-art", **{"aria-hidden": "true"}),
            html.Div(className="portfolio-masthead", children=[
                html.Button("Matheus Barbosa Faria", id="nav-inicio", n_clicks=0,
                            className="home-link", type="button", title="Voltar à página inicial"),
                html.Div(className="masthead-right", children=[
                    html.Span("PORTFÓLIO DIGITAL", className="masthead-label"),
                    html.Img(src=profile_url, className="profile-photo", alt="Matheus"),
                ]),
            ]),
            html.Div(className="hero-intro", children=[
                html.P("DESENVOLVIMENTO DE SOFTWARE & ANÁLISE DE DADOS", className="hero-eyebrow"),
                html.H1("MATHEUS", className="hero-name"),
                html.P("Ideias que se tornam soluções.", className="hero-caption"),
            ]),
            html.Div(className="navigation-shell", children=[
                html.Div(className="navigation-trigger", children=[
                    html.Button(html.Span("↓", **{"aria-hidden": "true"}),
                        id="btn-toggle-navigation", className="menu-toggle arrow-toggle",
                        n_clicks=0, type="button", title="Explorar o portfólio",
                        **{"aria-label": "Abrir navegação", "aria-controls": "top-navigation", "aria-expanded": "false"}),
                    html.Span("EXPLORAR PORTFÓLIO", className="navigation-caption"),
                ]),
                create_navigation(),
            ]),
            html.Div(className="hero-bottom", children=[
                html.Span("SOFTWARE · DADOS · EXPERIÊNCIAS"),
                html.Span("CRIAR. COMPREENDER. EVOLUIR."),
            ]),
        ]),
        html.Main(className="main-content", children=[
            html.Div(className="analysis-switcher", children=[
                html.P("ANÁLISES DE DADOS", className="page-eyebrow"),
                dcc.Tabs(id="analysis-selector", value="analise-dados", className="analysis-tabs",
                    parent_className="analysis-tabs-container", children=[
                        dcc.Tab(label=label, value=value, className="analysis-tab",
                                selected_className="analysis-tab selected")
                        for value, label in ANALYSIS_ITEMS
                    ]),
            ]),
            html.Div(id="tab-content-container"),
            html.Footer(className="page-footer", children=[
                html.Span("MATHEUS / PORTFÓLIO"),
                html.Span("Explorar dados. Encontrar perspectivas."),
            ]),
        ]),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="analysis-modal-title", children="Análise de dados"), close_button=True),
            dbc.ModalBody(id="analysis-modal-body", children=[]),
        ], id="analysis-modal", is_open=False, size="xl", centered=True, scrollable=True,
            backdrop=True, keyboard=True, className="analysis-modal"),
    ])
