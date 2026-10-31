"""Apresentação dos projetos e das experiências de desenvolvimento."""

from dash import html

from ..content import AI_APPROACH, PROJECTS


def page_heading(eyebrow, title, description):
    return html.Div(className="portfolio-heading", children=[
        html.P(eyebrow, className="page-eyebrow"),
        html.H1(title, className="header-title"),
        html.P(description, className="portfolio-intro"),
    ])


def project_links(project):
    """Acessos externos compartilhados entre Projetos e Qualificações."""
    links = []
    if project.get("demo_url"):
        links.append(html.A([
            html.I(className="fa-solid fa-arrow-up-right-from-square", **{"aria-hidden": "true"}),
            "Abrir demonstração",
        ], href=project["demo_url"], target="_blank", rel="noopener noreferrer",
            className="project-link project-link-primary",
            **{"aria-label": f"Abrir demonstração de {project['name']} (nova aba)"}))
    if project.get("github_url"):
        links.append(html.A([
            html.I(className="fa-brands fa-github", **{"aria-hidden": "true"}),
            "Ver no GitHub",
        ], href=project["github_url"], target="_blank", rel="noopener noreferrer",
            className="project-link",
            **{"aria-label": f"Ver {project['name']} no GitHub (nova aba)"}))
    if not links:
        return None
    return html.Div(links, className="project-links", role="group",
                    **{"aria-label": f"Acessos ao projeto {project['name']}"})


def _team_label(project):
    if not project.get("team"):
        return None
    return html.Span(f"{project['team']} · {project['team_size']} integrantes", className="project-team")


def _project_body(project, show_features=True):
    return [
        html.P(project["summary"], className="project-description"),
        html.P([html.Strong("Minha participação: "), project["role"]],
                 className="project-description") if project.get("role") else None,
        html.Div(className="project-technologies", children=[
            html.Span(technology) for technology in project["technologies"]
        ]),
        project_links(project),
        html.Ul([html.Li(feature) for feature in project["features"]], className="project-features")
        if show_features else None,
        html.P(project["note"], className="project-note") if project.get("note") else None,
        html.Div(className="experience-story", children=[
            html.H3("Minha experiência", className="experience-story-title"),
            html.P(project["experience"] or "Relato da experiência em preparação."),
        ]),
    ]


def _project_category(project):
    return html.Div(className="project-category", children=[
        html.Span(className="project-symbol", children=html.I(className=f"fa-solid {project['icon']}", **{"aria-hidden": "true"})),
        html.Span(project["category"]),
        _team_label(project),
        html.Span("DESTAQUE", className="project-featured-label") if project["featured"] else None,
    ])


def project_card(project, show_features=True):
    featured = " featured-project" if project["featured"] else ""
    return html.Article(className=f"project-card{featured}", children=[
        _project_category(project),
        html.H2(project["name"], className="project-title"),
        html.P(project["headline"], className="project-headline"),
        *_project_body(project, show_features),
    ])


def project_disclosure(project):
    featured = " featured-project" if project["featured"] else ""
    return html.Details(className=f"project-disclosure{featured}", open=False, children=[
        html.Summary(className="project-preview", children=[
            _project_category(project),
            html.Div(className="project-preview-heading", children=[
                html.H2(project["name"], className="project-title"),
                html.Span(className="project-disclosure-icon", **{"aria-hidden": "true"}),
            ]),
            html.P(project["headline"], className="project-headline"),
            html.Div(className="project-preview-bottom", children=[
                html.Span(" · ".join(project["technologies"][:3])),
                html.Span("Explorar projeto", className="project-explore-label"),
            ]),
        ]),
        html.Div(className="project-expanded", children=_project_body(project)),
    ])


def create_ai_approach():
    return html.Div(className="experience-story", children=[
        html.H2("Como desenvolvo com inteligência artificial", className="portfolio-section-title"),
        *[html.P(paragraph, className="project-description") for paragraph in AI_APPROACH],
    ])


def create_projects_layout():
    return html.Div(className="portfolio-page", children=[
        page_heading(
            "CONSTRUÇÃO & APRENDIZADO", "Projetos",
            "Selecione um projeto para conhecer a solução, minha participação e os aprendizados dessa experiência.",
        ),
        html.Div(className="projects-grid", children=[project_disclosure(project) for project in PROJECTS]),
        html.Section(className="project-card mt-4", children=create_ai_approach()),
    ])
