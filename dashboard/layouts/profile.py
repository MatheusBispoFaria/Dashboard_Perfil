"""Apresentação pessoal e qualificações reunidas em uma página própria."""

from dash import html

from .projects import create_ai_approach, page_heading

ABOUT_PARAGRAPHS = (
    "Estou cursando o bacharelado em Engenharia de Software na FIAP, com formação prevista para dezembro de 2028.",
    "Amo criar soluções e explorar novas possibilidades. Tenho facilidade em propor abordagens e conectar conhecimentos de diferentes contextos, mesmo quando preciso retomar e aprofundar a base técnica para colocá-las em prática.",
    "Tenho experiência na construção de aplicações digitais, com ênfase em APIs REST e análise de dados. Meu portfólio reúne a documentação dessas experiências e os links para os repositórios no GitHub, disponíveis na aba Projetos.",
    "Tenho grande interesse nas áreas financeira, de marketing, operações e logística. Meu principal objetivo é continuar aprendendo por meio da experiência prática, tanto nessas áreas quanto em outras que ofereçam oportunidades de desenvolvimento.",
)


def create_profile_layout():
    return html.Section(className="dash-card profile-summary", children=[
        html.H2("Matheus Bispo Faria Barbosa", className="project-title"),
        html.P("Software Engineering Student", className="profile-subtitle"),
        html.Div([html.P(text) for text in ABOUT_PARAGRAPHS], className="profile-copy"),
        html.H3("Contato e links", className="portfolio-section-title"),
        html.Div(className="project-links", children=[
            html.A("E-mail", href="mailto:matheusbispo0404@gmail.com", className="project-link"),
            html.A("LinkedIn", href="https://www.linkedin.com/in/matheus-barbosa-176a68355", target="_blank", rel="noopener noreferrer", className="project-link"),
            html.A("GitHub", href="https://github.com/MatheusBispoFaria", target="_blank", rel="noopener noreferrer", className="project-link"),
        ]),
    ])


def create_about_layout():
    return html.Div(className="about-page", children=[
        page_heading("TRAJETÓRIA & DESENVOLVIMENTO", "Quem Sou Eu",
                     "Minha formação, interesses e experiências construindo soluções."),
        create_profile_layout(),
    ])


def create_skills_layout():
    groups = {
        "Desenvolvimento": ["Python", "Java", "JavaScript", "React", "Node.js", "APIs REST", "Orientação a objetos"],
        "Dados e prática de projeto": ["Análise de dados", "Visualização de dados", "GitHub", "Figma", "Revisão de código", "Planejamento de desenvolvimento", "Trabalho em equipe"],
    }
    return html.Div(className="qualifications-page", children=[
        page_heading("FORMAÇÃO & COMPETÊNCIAS", "Qualificações",
                     "Conhecimentos aplicados nos projetos, formação acadêmica e aprendizado contínuo."),
        html.Div(className="qualifications-grid", children=[
            html.Section(className="dash-card", children=[
                html.H2("Competências", className="portfolio-section-title"),
                *[html.Div(className="qualification-skill-group", children=[
                    html.H3(title), html.Div([html.Span(skill) for skill in skills], className="project-technologies"),
                ]) for title, skills in groups.items()],
            ]),
            html.Section(className="dash-card", children=[
                html.H2("Formação acadêmica", className="portfolio-section-title"),
                html.H3("FIAP · Bacharelado em Engenharia de Software", className="qualification-degree"),
                html.P("Março de 2025 a dezembro de 2028 · Em andamento"),
                html.H3("Certificações", className="portfolio-section-title"),
                html.Ul([html.Li(text) for text in [
                    "Java: Primeira Aplicação", "Java Development", "Design Thinking - Process",
                    "Resolvendo Problemas com Matemática", "Soluções Tecnológicas Emergentes", "Formação Social e Sustentabilidade",
                ]]),
            ]),
        ]),
        html.Section(className="dash-card qualification-languages", children=[
            html.H2("Idiomas", className="portfolio-section-title"),
            html.P("Português nativo. Inglês intermediário, com boa leitura e interpretação de textos, compreensão de conversas e conversação simples. Fluência oral em desenvolvimento."),
        ]),
        html.Section(className="project-card qualification-ai", children=create_ai_approach()),
    ])


def create_qualifications_layout():
    """Compatibilidade com o identificador antigo da seção."""
    return create_skills_layout()
