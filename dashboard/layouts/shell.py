"""Estrutura principal, menu lateral e área de conteúdo."""

from dash import dcc, html

from ..config import DEFAULT_SECTION, NAV_ITEMS


def create_sidebar(profile_url):
    navigation = [html.Div(className="nav-divider")]
    for section, label, icon in NAV_ITEMS:
        navigation.extend([
            html.Div(
                [
                    html.I(className=f"fa-solid {icon} nav-icon"),
                    html.Span(label, className="nav-text"),
                ],
                id=f"nav-{section}",
                className=(
                    "nav-item active" if section == DEFAULT_SECTION else "nav-item"
                ),
                n_clicks=0,
                style={"cursor": "pointer"},
            ),
            html.Div(className="nav-divider"),
        ])

    return html.Div(id="sidebar", className="sidebar", children=[
        html.Div(className="sidebar-header", children=[
            html.Div(className="user-profile", children=[
                html.Img(src=profile_url, style={
                    "width": "38px", "height": "38px", "objectFit": "cover",
                    "borderRadius": "8px", "border": "2px solid #4379f2",
                }),
                html.Div("MATHEUS", className="username"),
            ]),
            html.Button(
                html.I(className="fa-solid fa-bars"),
                id="btn-toggle-sidebar",
                className="toggle-btn",
                n_clicks=0,
                style={
                    "border": "none", "background": "transparent",
                    "color": "#fff", "fontSize": "18px",
                },
            ),
        ]),
        *navigation,
    ])


def create_main_layout(profile_url):
    return html.Div(className="dashboard-wrapper", children=[
        dcc.Store(id="active-section", data=DEFAULT_SECTION),
        create_sidebar(profile_url),
        html.Div(className="main-content", children=[
            html.H1("Dashboard Profissional", className="header-title"),
            html.Div(
                "PORTFÓLIO E CENSUS INCOME DATASET",
                className="header-subtitle mb-4",
            ),
            html.Div(id="tab-content-container"),
        ]),
    ])
