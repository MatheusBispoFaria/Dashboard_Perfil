"""Telas de apresentação, qualificações e competências."""

from dash import html
import dash_bootstrap_components as dbc

from ..theme import C_NAVY


def create_profile_layout():
    return html.Div(className="dash-card p-4", children=[
        html.Div([
            html.H3("Matheus Barbosa Faria", className="fw-bold mb-1", style={"color": C_NAVY}),
            html.P("Software Engineering Student | Full Stack Developer | IoT Systems", className="text-muted fw-semibold mb-4"),
        
            html.H5("Resumo Profissional", className="fw-bold text-primary mb-2"),
            html.P(
                "Sou estudante de Engenharia de Software (formação prevista para 2028), com interesse em atuar "
                "na área financeira e em sistemas que exigem alta confiabilidade e organização técnica. "
                "Venho desenvolvendo projetos práticos em desenvolvimento de software, com experiência em JavaScript, "
                "Node.js e Python, estruturando APIs, integração cliente-servidor e lógica de sistemas. "
                "Atualmente, estou aprofundando meus estudos em Java, com foco em arquitetura, boas práticas e "
                "desenvolvimento orientado a sistemas robustos.",
                className="text-secondary mb-4"
            ),

            html.H5("Contato e Links", className="fw-bold text-primary mb-2"),
            html.Ul([
                html.Li([html.I(className="fa-solid fa-envelope me-2 text-muted"), html.Strong("E-mail: "), html.A("matheusbispo0404@gmail.com", href="mailto:matheusbispo0404@gmail.com")]),
                html.Li([html.I(className="fa-brands fa-linkedin me-2 text-muted"), html.Strong("LinkedIn: "), html.A("linkedin.com/in/matheus-barbosa-176a68355", href="https://www.linkedin.com/in/matheus-barbosa-176a68355", target="_blank")]),
                html.Li([html.I(className="fa-brands fa-github me-2 text-muted"), html.Strong("GitHub / Portfolio: "), html.A("github.com/Matheus Bispo Faria", href="https://github.com", target="_blank")]),
            ], className="list-unstyled text-secondary")
        ])
    ])


def create_qualifications_layout():
    return html.Div(className="dash-card p-4", children=[
        html.H3("Minhas Qualificações", className="fw-bold mb-4", style={"color": C_NAVY}),
    
        html.H5([html.I(className="fa-solid fa-graduation-cap me-2 text-primary"), "Formação Acadêmica"], className="fw-bold text-primary mb-2"),
        html.Div([
            html.H6("FIAP — Bacharelado em Computer Software Engineering", className="fw-bold mb-1"),
            html.P("Março de 2025 – Dezembro de 2028", className="text-muted small mb-4")
        ]),

        html.H5([html.I(className="fa-solid fa-certificate me-2 text-primary"), "Certificações"], className="fw-bold text-primary mb-2"),
        html.Ul([
            html.Li("Java: Primeira Aplicação"),
            html.Li("Resolvendo Problemas com Matemática"),
            html.Li("Soluções Tecnológicas Emergentes"),
            html.Li("Java Development"),
            html.Li("Formação Social e Sustentabilidade"),
        ], className="text-secondary")
    ])


def create_skills_layout():
    return html.Div(className="dash-card p-4", children=[
        html.H3("Skills e Competências", className="fw-bold mb-4", style={"color": C_NAVY}),
    
        dbc.Row([
            dbc.Col([
                html.H5([html.I(className="fa-solid fa-code me-2 text-primary"), "Principais Competências"], className="fw-bold text-primary mb-3"),
                html.Div([
                    html.Span("Java", className="badge bg-primary me-2 mb-2 p-2"),
                    html.Span("JavaScript", className="badge bg-primary me-2 mb-2 p-2"),
                    html.Span("Node.js", className="badge bg-primary me-2 mb-2 p-2"),
                    html.Span("Python", className="badge bg-primary me-2 mb-2 p-2"),
                    html.Span("POO (Orientação a Objetos)", className="badge bg-primary me-2 mb-2 p-2"),
                    html.Span("Pensamento Crítico", className="badge bg-primary me-2 mb-2 p-2"),
                ])
            ], md=6),
            dbc.Col([
                html.H5([html.I(className="fa-solid fa-globe me-2 text-primary"), "Idiomas"], className="fw-bold text-primary mb-3"),
                html.Ul([
                    html.Li("Português (Nativo / Bilíngue)"),
                    html.Li("Inglês B1 (Profissional / Working)"),
                ], className="text-secondary")
            ], md=6)
        ])
    ])
