import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ---------------------------------------------------------------
# Carregamento e Preparação dos Dados
# ---------------------------------------------------------------
df = pd.read_csv("adult_clean.csv")

df["income"] = df["income"].astype(str).str.strip()
df["sex"] = df["sex"].astype(str).str.strip()
df["occupation"] = df["occupation"].astype(str).str.strip()
df["renda_alta"] = (df["income"] == ">50K").astype(int)

df["workclass"] = df["workclass"].astype(str).str.strip() if "workclass" in df.columns else "N/A"
df["education"] = df["education"].astype(str).str.strip() if "education" in df.columns else "N/A"

# ---------------------------------------------------------------
# Configuração Visual Ajustada
# ---------------------------------------------------------------
layout_clean = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=15, r=15, t=15, b=15),
    font=dict(family="-apple-system, BlinkMacSystemFont, sans-serif", size=11, color="#475569"),
    xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
)

C_NAVY = "#0f172a"
C_BLUE = "#4379f2"
C_LIGHT_BLUE = "#709cfd"
C_CYAN = "#00c49f"

# ---------------------------------------------------------------
# Componentes de Filtro (UI)
# ---------------------------------------------------------------
filtros_layout = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label("Renda", className="card-title-sm"),
                dcc.Dropdown(
                    id="filtro-renda",
                    options=[{"label": i, "value": i} for i in df["income"].unique()],
                    multi=True,
                    placeholder="Todas"
                )
            ], width=2),
            dbc.Col([
                html.Label("Vínculo", className="card-title-sm"),
                dcc.Dropdown(
                    id="filtro-vinculo",
                    options=[{"label": i, "value": i} for i in df["workclass"].unique() if i != 'nan'],
                    multi=True,
                    placeholder="Todos"
                )
            ], width=2),
            dbc.Col([
                html.Label("Escolaridade", className="card-title-sm"),
                dcc.Dropdown(
                    id="filtro-escolaridade",
                    options=[{"label": i, "value": i} for i in df["education"].unique() if i != 'nan'],
                    multi=True,
                    placeholder="Todas"
                )
            ], width=2),
            dbc.Col([
                html.Label("Idade", className="card-title-sm"),
                dcc.RangeSlider(
                    id="filtro-idade",
                    min=df["age"].min(), max=df["age"].max(),
                    value=[df["age"].min(), df["age"].max()],
                    marks=None, tooltip={"placement": "bottom", "always_visible": True}
                )
            ], width=3),
            dbc.Col([
                html.Label("Jornada (Horas)", className="card-title-sm"),
                dcc.RangeSlider(
                    id="filtro-jornada",
                    min=df["hours_per_week"].min(), max=df["hours_per_week"].max(),
                    value=[df["hours_per_week"].min(), df["hours_per_week"].max()],
                    marks=None, tooltip={"placement": "bottom", "always_visible": True}
                )
            ], width=3),
        ], className="align-items-center")
    ]),
    className="mb-4 dash-card", style={"padding": "10px"}
)

# ---------------------------------------------------------------
# Seções Preenchidas com Dados do Currículo (Profile.pdf)
# ---------------------------------------------------------------
layout_quem_sou_eu = html.Div(className="dash-card p-4", children=[
    html.Div([
        html.H3("Matheus Barbosa Faria", className="fw-bold mb-1", style={"color": C_NAVY}),
        html.P("Software Engineering Student | Full Stack Developer | IoT Systems", className="text-muted fw-semibold mb-4"),
        
        html.H5("Resumo Profissional", className="fw-bold text-primary mb-2"),
        html.P(
            "Sou estudante de Engenharia de Software (formação prevista para 2028), com interesse em atuar "
            "na área financeira e em sistemas que exigem alta confiabilidade e organização técnica[cite: 2]. "
            "Venho desenvolvendo projetos práticos em desenvolvimento de software, com experiência em JavaScript, "
            "Node.js e Python, estruturando APIs, integração cliente-servidor e lógica de sistemas[cite: 2]. "
            "Atualmente, estou aprofundando meus estudos em Java, com foco em arquitetura, boas práticas e "
            "desenvolvimento orientado a sistemas robustos[cite: 2].",
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

layout_qualificacoes = html.Div(className="dash-card p-4", children=[
    html.H3("Minhas Qualificações", className="fw-bold mb-4", style={"color": C_NAVY}),
    
    html.H5([html.I(className="fa-solid fa-graduation-cap me-2 text-primary"), "Formação Acadêmica"], className="fw-bold text-primary mb-2"),
    html.Div([
        html.H6("FIAP — Bacharelado em Computer Software Engineering", className="fw-bold mb-1"),
        html.P("Março de 2025 – Dezembro de 2028[cite: 2]", className="text-muted small mb-4")
    ]),

    html.H5([html.I(className="fa-solid fa-certificate me-2 text-primary"), "Certificações"], className="fw-bold text-primary mb-2"),
    html.Ul([
        html.Li("Java: Primeira Aplicação[cite: 2]"),
        html.Li("Resolvendo Problemas com Matemática[cite: 2]"),
        html.Li("Soluções Tecnológicas Emergentes[cite: 2]"),
        html.Li("Java Development[cite: 2]"),
        html.Li("Formação Social e Sustentabilidade[cite: 2]"),
    ], className="text-secondary")
])

layout_skills = html.Div(className="dash-card p-4", children=[
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
                html.Li("Português (Nativo / Bilíngue)[cite: 2]"),
                html.Li("Inglês B1 (Profissional / Working)[cite: 2]"),
            ], className="text-secondary")
        ], md=6)
    ])
])

layout_analise_dados = html.Div([
    filtros_layout,
    
    # Linha 1
    dbc.Row(className="mb-4", children=[
        dbc.Col(width=6, children=[
            html.Div(className="dash-card", children=[
                html.Div("DISTRIBUIÇÃO DE OCUPAÇÕES", className="card-title-sm"),
                dcc.Graph(id="graph-ocupacoes", config={'displayModeBar': False})
            ])
        ]),
        dbc.Col(width=3, children=[
            html.Div(className="dash-card", children=[
                html.Div("DISTRIBUIÇÃO DE RENDA", className="card-title-sm"),
                dcc.Graph(id="graph-renda", config={'displayModeBar': False})
            ])
        ]),
        dbc.Col(width=3, children=[
            html.Div(className="dash-card", children=[
                html.Div("GÊNERO NA BASE", className="card-title-sm"),
                dcc.Graph(id="graph-genero", config={'displayModeBar': False})
            ])
        ]),
    ]),

    # Linha 2
    dbc.Row(className="mb-4", children=[
        dbc.Col(width=4, children=[
            html.Div(className="dash-card", children=[
                html.Div("DENSIDADE DE IDADE POR RENDA", className="card-title-sm"),
                dcc.Graph(id="graph-idade-renda", config={'displayModeBar': False})
            ])
        ]),
        dbc.Col(width=4, children=[
            html.Div(className="dash-card", children=[
                html.Div("MÉDIA DE HORAS/SEMANA POR IDADE", className="card-title-sm"),
                dcc.Graph(id="graph-horas-idade", config={'displayModeBar': False})
            ])
        ]),
        dbc.Col(width=4, children=[
            html.Div(className="dash-card", children=[
                html.Div("% RENDA ALTA GLOBAL (>50K)", className="card-title-sm"),
                dcc.Graph(id="graph-velocimetro", config={'displayModeBar': False})
            ])
        ]),
    ]),

    # Linha 3
    dbc.Row(children=[
        dbc.Col(width=4, children=[
            html.Div(className="dash-card d-flex flex-row align-items-center", children=[
                html.Div(style={"width": "100px"}, children=[
                    dcc.Graph(id="graph-donut-homens", config={'displayModeBar': False})
                ]),
                html.Div(className="ms-3", children=[
                    html.Div("HOMENS (>50K)", className="card-title-sm", style={"border": "none", "margin": 0, "padding": 0}),
                    html.P("Taxa de alta renda no grupo masculino", style={"fontSize": "12px", "color": "#64748b", "margin": 0})
                ])
            ])
        ]),
        dbc.Col(width=4, children=[
            html.Div(className="dash-card d-flex flex-row align-items-center", children=[
                html.Div(style={"width": "100px"}, children=[
                    dcc.Graph(id="graph-donut-mulheres", config={'displayModeBar': False})
                ]),
                html.Div(className="ms-3", children=[
                    html.Div("MULHERES (>50K)", className="card-title-sm", style={"border": "none", "margin": 0, "padding": 0}),
                    html.P("Taxa de alta renda no grupo feminino", style={"fontSize": "12px", "color": "#64748b", "margin": 0})
                ])
            ])
        ]),
        dbc.Col(width=4, children=[
            html.Div(className="dash-card justify-content-center", children=[
                html.Div("TOP ESCOLARIDADE (>50K)", className="card-title-sm mb-3"),
                html.Div(id="top-escolaridade-container") 
            ])
        ]),
    ]),
])

# ---------------------------------------------------------------
# Inicialização do App
# ---------------------------------------------------------------
FA_CDN = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, FA_CDN], suppress_callback_exceptions=True)

# ---------------------------------------------------------------
# Layout Principal com Foto de Perfil Dinâmica
# ---------------------------------------------------------------
app.layout = html.Div(className="dashboard-wrapper", children=[
    
    dcc.Store(id="active-section", data="analise-dados"),

    # Sidebar Retrátil
    html.Div(id="sidebar", className="sidebar", children=[
        html.Div(className="sidebar-header", children=[
            html.Div(className="user-profile", children=[
                html.Img(src="/assets/profile.jpg", style={
                    "width": "38px", "height": "38px", "objectFit": "cover", 
                    "borderRadius": "8px", "border": "2px solid #4379f2"
                }),
                html.Div("MATHEUS", className="username"),
            ]),
            html.Button(html.I(className="fa-solid fa-bars"), id="btn-toggle-sidebar", className="toggle-btn", n_clicks=0, style={"border": "none", "background": "transparent", "color": "#fff", "fontSize": "18px"}),
        ]),
        
        html.Div(className="nav-divider"),
        
        html.Div([
            html.I(className="fa-solid fa-chart-line nav-icon"), 
            html.Span("Análise de Dados", className="nav-text")
        ], id="nav-analise-dados", className="nav-item active", n_clicks=0, style={"cursor": "pointer"}),
        
        html.Div(className="nav-divider"),
        
        html.Div([
            html.I(className="fa-solid fa-user nav-icon"), 
            html.Span("Quem Sou Eu", className="nav-text")
        ], id="nav-quem-sou-eu", className="nav-item", n_clicks=0, style={"cursor": "pointer"}),
        
        html.Div(className="nav-divider"),
        
        html.Div([
            html.I(className="fa-solid fa-graduation-cap nav-icon"), 
            html.Span("Qualificações", className="nav-text")
        ], id="nav-qualificacoes", className="nav-item", n_clicks=0, style={"cursor": "pointer"}),
        
        html.Div(className="nav-divider"),
        
        html.Div([
            html.I(className="fa-solid fa-lightbulb nav-icon"), 
            html.Span("Skills", className="nav-text")
        ], id="nav-skills", className="nav-item", n_clicks=0, style={"cursor": "pointer"}),
        
        html.Div(className="nav-divider"),
    ]),

    # Conteúdo Principal
    html.Div(className="main-content", children=[
        html.H1("Dashboard de Dados", className="header-title"),
        html.Div("PORTFÓLIO E CENSUS INCOME DATASET", className="header-subtitle mb-4"),

        html.Div(id="tab-content-container")
    ])
])

# ---------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------

@app.callback(
    Output("sidebar", "className"),
    Input("btn-toggle-sidebar", "n_clicks"),
    State("sidebar", "className"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, current_class):
    if "collapsed" in current_class:
        return "sidebar"
    return "sidebar collapsed"

@app.callback(
    [Output("active-section", "data"),
     Output("nav-analise-dados", "className"),
     Output("nav-quem-sou-eu", "className"),
     Output("nav-qualificacoes", "className"),
     Output("nav-skills", "className")],
    [Input("nav-analise-dados", "n_clicks"),
     Input("nav-quem-sou-eu", "n_clicks"),
     Input("nav-qualificacoes", "n_clicks"),
     Input("nav-skills", "n_clicks")],
    State("active-section", "data")
)
def update_active_section(btn1, btn2, btn3, btn4, current_section):
    ctx = dash.callback_context

    if not ctx.triggered:
        return "analise-dados", "nav-item active", "nav-item", "nav-item", "nav-item"
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == "nav-analise-dados":
            return "analise-dados", "nav-item active", "nav-item", "nav-item", "nav-item"
        elif button_id == "nav-quem-sou-eu":
            return "quem-sou-eu", "nav-item", "nav-item active", "nav-item", "nav-item"
        elif button_id == "nav-qualificacoes":
            return "qualificacoes", "nav-item", "nav-item", "nav-item active", "nav-item"
        elif button_id == "nav-skills":
            return "skills", "nav-item", "nav-item", "nav-item", "nav-item active"
            
    return current_section, "nav-item", "nav-item", "nav-item", "nav-item"

@app.callback(
    Output("tab-content-container", "children"),
    Input("active-section", "data")
)
def render_content(active_section):
    if active_section == "quem-sou-eu":
        return layout_quem_sou_eu
    elif active_section == "qualificacoes":
        return layout_qualificacoes
    elif active_section == "skills":
        return layout_skills
    elif active_section == "analise-dados":
        return layout_analise_dados
    return layout_analise_dados

@app.callback(
    [Output("graph-ocupacoes", "figure"),
     Output("graph-renda", "figure"),
     Output("graph-genero", "figure"),
     Output("graph-idade-renda", "figure"),
     Output("graph-horas-idade", "figure"),
     Output("graph-velocimetro", "figure"),
     Output("graph-donut-homens", "figure"),
     Output("graph-donut-mulheres", "figure"),
     Output("top-escolaridade-container", "children")],
    [Input("filtro-renda", "value"),
     Input("filtro-vinculo", "value"),
     Input("filtro-escolaridade", "value"),
     Input("filtro-idade", "value"),
     Input("filtro-jornada", "value")],
    prevent_initial_call=False
)
def update_dashboard(filtro_renda, filtro_vinculo, filtro_escolaridade, filtro_idade, filtro_jornada):
    dff = df.copy()

    if filtro_renda:
        dff = dff[dff["income"].isin(filtro_renda)]
    if filtro_vinculo:
        dff = dff[dff["workclass"].isin(filtro_vinculo)]
    if filtro_escolaridade:
        dff = dff[dff["education"].isin(filtro_escolaridade)]
    if filtro_idade:
        dff = dff[(dff["age"] >= filtro_idade[0]) & (dff["age"] <= filtro_idade[1])]
    if filtro_jornada:
        dff = dff[(dff["hours_per_week"] >= filtro_jornada[0]) & (dff["hours_per_week"] <= filtro_jornada[1])]

    if dff.empty:
        empty_fig = go.Figure().update_layout(**layout_clean)
        return [empty_fig] * 8 + [html.Div("Sem dados para esta seleção.")]

    occ_counts = dff[dff["occupation"] != "nan"]["occupation"].value_counts().head(10).reset_index()
    fig_bar = px.bar(occ_counts, x="occupation", y="count", color_discrete_sequence=[C_NAVY])
    fig_bar.update_layout(**layout_clean, height=230)
    fig_bar.update_traces(marker_line_width=0, hovertemplate="%{x}: <b>%{y}</b>")
    fig_bar.update_xaxes(title="", tickangle=-35)
    fig_bar.update_yaxes(title="")

    income_counts = dff["income"].value_counts().reset_index()
    fig_pie = px.pie(income_counts, values="count", names="income", hole=0,
                     color_discrete_map={"<=50K": C_BLUE, ">50K": C_CYAN})
    fig_pie.update_layout(**layout_clean, height=230, showlegend=True, 
                          legend=dict(orientation="h", y=-0.1, x=0.2))
    fig_pie.update_traces(textinfo="percent+label")

    sex_counts = dff["sex"].value_counts().reset_index()
    fig_donut = px.pie(sex_counts, values="count", names="sex", hole=0.68,
                       color_discrete_map={"Male": C_NAVY, "Female": C_LIGHT_BLUE})
    fig_donut.update_layout(**layout_clean, height=230, showlegend=False)
    fig_donut.add_annotation(text="GÊNERO", x=0.5, y=0.5, font_size=12, font_weight="bold", showarrow=False, font_color="#64748b")
    fig_donut.update_traces(textinfo="percent+label")

    age_income = dff.groupby(["age", "income"]).size().reset_index(name="count")
    fig_area = px.area(age_income, x="age", y="count", color="income", 
                       color_discrete_map={"<=50K": C_LIGHT_BLUE, ">50K": C_NAVY})
    fig_area.update_layout(**layout_clean, height=200, showlegend=False)
    fig_area.update_xaxes(title="", showgrid=False)
    fig_area.update_yaxes(title="")

    hours_age = dff.groupby("age")["hours_per_week"].mean().reset_index()
    fig_line = px.line(hours_age, x="age", y="hours_per_week", markers=True)
    fig_line.update_traces(line_color=C_BLUE, marker=dict(size=4, color=C_CYAN))
    fig_line.update_layout(**layout_clean, height=200, showlegend=False)
    fig_line.update_xaxes(title="", showgrid=False)
    fig_line.update_yaxes(title="")

    pct_alta = dff["renda_alta"].mean() * 100
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_alta,
        number={'suffix': "%", 'valueformat': ".1f", 'font': {'size': 26, 'color': C_NAVY, 'weight': 'bold'}},
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': C_CYAN, 'thickness': 0.75},
            'bgcolor': "#e2e8f0",
            'steps': [
                {'range': [0, 50], 'color': C_LIGHT_BLUE},
                {'range': [50, 100], 'color': C_NAVY}
            ]
        }
    ))
    fig_gauge.update_layout(**layout_clean, height=200)

    male_data = dff[dff["sex"] == "Male"]
    male_pct = male_data["renda_alta"].mean() * 100 if not male_data.empty else 0
    fig_p_male = go.Figure(go.Pie(values=[male_pct, 100-male_pct], hole=0.75, marker_colors=[C_CYAN, "#e2e8f0"]))
    fig_p_male.update_layout(**layout_clean, height=120, showlegend=False)
    fig_p_male.add_annotation(text=f"{male_pct:.1f}%", x=0.5, y=0.5, font_size=15, font_weight="bold", showarrow=False, font_color=C_CYAN)

    female_data = dff[dff["sex"] == "Female"]
    female_pct = female_data["renda_alta"].mean() * 100 if not female_data.empty else 0
    fig_p_female = go.Figure(go.Pie(values=[female_pct, 100-female_pct], hole=0.75, marker_colors=[C_BLUE, "#e2e8f0"]))
    fig_p_female.update_layout(**layout_clean, height=120, showlegend=False)
    fig_p_female.add_annotation(text=f"{female_pct:.1f}%", x=0.5, y=0.5, font_size=15, font_weight="bold", showarrow=False, font_color=C_BLUE)

    top_edu = dff.groupby("education")["renda_alta"].mean().sort_values(ascending=False).head(3) * 100
    edu_labels = top_edu.index.tolist()
    edu_vals = top_edu.values.tolist()
    colors = [C_CYAN, C_BLUE, C_NAVY]
    
    html_educacao = []
    for i in range(len(edu_labels)):
        html_educacao.append(
            html.Div([
                html.Div(className="d-flex justify-content-between mb-1", style={"fontSize": "11px", "fontWeight": "bold", "color": colors[i]}, children=[
                    html.Span(edu_labels[i]), html.Span(f"{edu_vals[i]:.1f}%")
                ]),
                html.Div(className="progress-bar-container", children=[
                    html.Div(className="progress-track", children=[
                        html.Div(className="progress-fill", style={"width": f"{edu_vals[i]}%", "backgroundColor": colors[i]})
                    ])
                ])
            ])
        )

    return fig_bar, fig_pie, fig_donut, fig_area, fig_line, fig_gauge, fig_p_male, fig_p_female, html_educacao

if __name__ == "__main__":
    app.run(debug=True, port=8050)