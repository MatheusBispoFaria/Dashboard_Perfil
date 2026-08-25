import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# ---------------------------------------------------------------
# Carregamento e Preparação dos Dados
# ---------------------------------------------------------------
df = pd.read_csv("adult_clean.csv")
df["income"] = df["income"].str.strip()
df["renda_alta"] = (df["income"] == ">50K").astype(int)

# Métricas globais
total_registros = len(df)
pct_alta_renda = df["renda_alta"].mean() * 100
idade_media = df["age"].mean()
horas_media = df["hours_per_week"].mean()

# Estilo Padrão para os Gráficos
layout_transparente = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

cores_renda = {"<=50K": "#0ba39c", ">50K": "#ff7e5f"}

# ---------------------------------------------------------------
# Construção dos Gráficos
# ---------------------------------------------------------------
# 1. Gráfico Central Destaque (Histograma de Idade Expandido)
fig_central_idade = px.histogram(
    df, x="age", color="income", barmode="overlay", nbins=45,
    color_discrete_map=cores_renda, opacity=0.75,
    labels={"age": "Idade (Anos)", "income": "Renda"}
)
fig_central_idade.update_layout(**layout_transparente)
fig_central_idade.update_layout(height=670, xaxis_title="Faixa Etária", yaxis_title="Total de Clientes")

# 2. Boxplot (Horas/Semana) - Lateral Esquerda
fig_box_horas = px.box(
    df, x="income", y="hours_per_week", color="income",
    color_discrete_map=cores_renda
)
fig_box_horas.update_layout(**layout_transparente, height=300)
fig_box_horas.update_traces(showlegend=False)

# 3. Pizza (Tipo de Vínculo / Workclass) - Lateral Esquerda
work_counts = df["workclass"].value_counts().head(5).reset_index()
work_counts.columns = ["workclass", "count"]
fig_pie_work = px.pie(
    work_counts, names="workclass", values="count",
    color_discrete_sequence=["#0ba39c", "#ff7e5f", "#f7b733", "#a18cd1", "#203a43"],
    hole=0.4
)
fig_pie_work.update_layout(**layout_transparente, height=300)
fig_pie_work.update_traces(textinfo="percent+label", showlegend=False)

# 4. Barras Escolaridade - Lateral Direita
by_edu = df.groupby("education")["renda_alta"].mean().reset_index()
by_edu["renda_alta"] *= 100
by_edu = by_edu.sort_values("renda_alta").tail(7)
fig_bar_edu = px.bar(
    by_edu, x="renda_alta", y="education", orientation="h",
    color="renda_alta", color_continuous_scale="Teal"
)
fig_bar_edu.update_layout(**layout_transparente, coloraxis_showscale=False, height=300)

# 5. Barras Ocupação - Lateral Direita
by_occ = df.dropna(subset=["occupation"]).groupby("occupation")["renda_alta"].mean().reset_index()
by_occ["renda_alta"] *= 100
by_occ = by_occ.sort_values("renda_alta").tail(7)
fig_bar_occ = px.bar(
    by_occ, x="renda_alta", y="occupation", orientation="h",
    color="renda_alta", color_continuous_scale="Sunset"
)
fig_bar_occ.update_layout(**layout_transparente, coloraxis_showscale=False, height=300)

# 6. Matriz de Correlação (Página 2)
numeric_cols = [c for c in df.select_dtypes(include="number").columns if c != "renda_alta"]
corr = df[numeric_cols].corr()
fig_corr = px.imshow(
    corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r"
)
fig_corr.update_layout(**layout_transparente, height=400)

# ---------------------------------------------------------------
# Layout Principal com Abas
# ---------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
app.title = "Income & Credit Analytics"

def criar_kpi(titulo, valor, icone, classe_gradiente):
    return html.Div(className=f"kpi-card {classe_gradiente}", children=[
        html.I(className=f"{icone} kpi-icon"),
        html.H3(valor, className="kpi-value"),
        html.P(titulo, className="kpi-title")
    ])

# Conteúdo das Páginas/Abas
tab1_content = html.Div([
    html.H4("1. Visão Geral da Base de Dados", className="mt-3 mb-3"),
    dbc.Row([
        dbc.Col([
            html.Div(className="chart-card", children=[
                html.Div("Amostra dos Dados Registrados", className="chart-title"),
                dash_table.DataTable(
                    data=df.head(8).to_dict('records'),
                    columns=[{"name": i, "id": i} for i in ['age', 'workclass', 'education', 'occupation', 'hours_per_week', 'income']],
                    style_header={'backgroundColor': '#1b1e2b', 'color': 'white', 'fontWeight': 'bold'},
                    style_cell={'backgroundColor': '#262b3d', 'color': 'white', 'fontSize': '12px'},
                    style_table={'overflowX': 'auto'}
                )
            ])
        ], width=12)
    ])
], className="p-2")

tab2_content = html.Div([
    html.H4("2. Análise Exploratória e Correlações", className="mt-3 mb-3"),
    dbc.Row([
        dbc.Col([
            html.Div(className="chart-card", children=[
                html.Div("Matriz de Correlação entre Variáveis Numéricas", className="chart-title"),
                dcc.Graph(figure=fig_corr, config={'displayModeBar': False})
            ])
        ], width=12)
    ])
], className="p-2")

tab3_content = html.Div([
    html.H4("3. Perfil de Risco e Crédito", className="mt-3 mb-3"),
    dbc.Row([
        dbc.Col([
            html.Div(className="chart-card", children=[
                html.Div("Proporção de Renda Alta por Escolaridade", className="chart-title"),
                dcc.Graph(figure=fig_bar_edu, config={'displayModeBar': False})
            ])
        ], width=6),
        dbc.Col([
            html.Div(className="chart-card", children=[
                html.Div("Proporção de Renda Alta por Ocupação", className="chart-title"),
                dcc.Graph(figure=fig_bar_occ, config={'displayModeBar': False})
            ])
        ], width=6)
    ])
], className="p-2")

# ABA 4: DASHBOARD COM GRÁFICO CENTRAL
tab4_content = html.Div([
    # Linha de KPIs
    dbc.Row([
        dbc.Col(criar_kpi("Total Clientes", f"{total_registros:,}".replace(",", "."), "fas fa-database", "grad-teal"), width=3),
        dbc.Col(criar_kpi("Taxa > 50K", f"{pct_alta_renda:.1f}%", "fas fa-chart-line", "grad-orange"), width=3),
        dbc.Col(criar_kpi("Idade Média", f"{idade_media:.0f} anos", "fas fa-user-clock", "grad-yellow"), width=3),
        dbc.Col(criar_kpi("Jornada Média", f"{horas_media:.0f} h/sem", "fas fa-briefcase", "grad-purple"), width=3),
    ]),

    # GRID DE 3 COLUNAS (LATERAL ESQUERDA - CENTRAL - LATERAL DIREITA)
    dbc.Row([
        # Coluna Esquerda (Width=3)
        dbc.Col([
            html.Div(className="chart-card", children=[
                html.Div("Jornada Semanal (BoxPlot)", className="chart-title"),
                dcc.Graph(figure=fig_box_horas, config={'displayModeBar': False})
            ]),
            html.Div(className="chart-card", children=[
                html.Div("Top Vínculos de Trabalho", className="chart-title"),
                dcc.Graph(figure=fig_pie_work, config={'displayModeBar': False})
            ]),
        ], width=3),

        # Coluna Central Destaque (Width=6)
        dbc.Col([
            html.Div(className="chart-card-center", children=[
                html.Div("🎯 Análise Central: Distribuição Etária por Faixa de Renda", className="chart-title-center"),
                dcc.Graph(figure=fig_central_idade, config={'displayModeBar': False})
            ])
        ], width=6),

        # Coluna Direita (Width=3)
        dbc.Col([
            html.Div(className="chart-card", children=[
                html.Div("Escolaridades em Destaque", className="chart-title"),
                dcc.Graph(figure=fig_bar_edu, config={'displayModeBar': False})
            ]),
            html.Div(className="chart-card", children=[
                html.Div("Ocupações em Destaque", className="chart-title"),
                dcc.Graph(figure=fig_bar_occ, config={'displayModeBar': False})
            ]),
        ], width=3),
    ])
], className="p-2")

# App Layout Completo
app.layout = dbc.Container([
    # Header
    html.Div([
        html.H2("Income Analytics System", style={"fontWeight": "300", "marginTop": "20px"}),
        html.P("Plataforma Integrada de Análise de Renda e Perfil de Crédito", style={"color": "#8b94a5", "marginBottom": "20px"})
    ]),

    # Navegação por Abas
    dbc.Tabs([
        dbc.Tab(tab1_content, label="1. Visão Geral", tab_id="tab-1"),
        dbc.Tab(tab2_content, label="2. Análise Exploratória", tab_id="tab-2"),
        dbc.Tab(tab3_content, label="3. Perfil de Risco", tab_id="tab-3"),
        dbc.Tab(tab4_content, label="4. Dashboard Executivo", tab_id="tab-4", active_tab_style={"fontWeight": "bold"}),
    ], id="tabs", active_tab="tab-4"),

], fluid=True, style={"padding": "0 30px 30px 30px"})

# ---------------------------------------------------------------
# Execução Local
# ---------------------------------------------------------------
server = app.server

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)