"""Contexto do estudo, seis gráficos e consulta aos registros selecionados."""

from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc

from ..interpretations import SOURCE, base_findings
from ..socioeconomic import TABLE_COLUMNS
from .cards import create_chart_card
from .filters import create_filters


def create_analysis_layout(data):
    return html.Div(className="analysis-page socio-page", children=[
        html.Div(className="page-heading", children=[
            html.Div([
                html.P("ADULT · UCI · ESTADOS UNIDOS · 1994", className="page-eyebrow"),
                html.H1("Renda e perfil socioeconômico", className="header-title"),
                html.P("Renda anual, escolaridade, ocupação e jornada de trabalho em uma amostra histórica de 32.561 pessoas.", className="analysis-intro"),
            ]),
            html.Span(id="selection-summary", className="selection-summary", **{"aria-live": "polite"}),
        ]),
        html.Div(className="socio-toolbar", children=[
            html.Button([html.I(className="fa-solid fa-bars", **{"aria-hidden": "true"}), "Filtros"],
                        id="socio-toggle-filters", n_clicks=0, type="button", className="socio-panel-toggle",
                        **{"aria-expanded": "false", "aria-controls": "socio-filters-panel"}),
            html.Button([html.I(className="fa-solid fa-circle-info", **{"aria-hidden": "true"}), "Sobre a base"],
                        id="socio-toggle-description", n_clicks=0, type="button", className="socio-panel-toggle",
                        **{"aria-expanded": "false", "aria-controls": "socio-description-panel"}),
        ]),
        dbc.Collapse(html.Section(className="socio-study-panel", children=[
            html.H2("Sobre o estudo e a escolha da base", className="portfolio-section-title"),
            html.Div(className="socio-context-copy", children=[
                html.P("Desenvolvi este estudo em um checkpoint da FIAP, em 2026. A proposta era criar um portfólio digital que reunisse minha apresentação, qualificações e projetos, com um dashboard dedicado à análise de um tema de interesse."),
                html.P("Por recomendação do professor, escolhi a base Adult (Census Income), disponível no repositório UCI. Publicada em 1996, ela reúne dados socioeconômicos dos Estados Unidos referentes a 1994. Neste projeto, utilizei 32.561 registros para explorar as relações entre renda anual, escolaridade, idade, ocupação e jornada de trabalho."),
                html.P("Meu interesse pelo setor financeiro motivou a investigação de como esses perfis se relacionam com a renda. O objetivo foi aplicar conhecimentos de análise de dados e visualização para comparar grupos e formular perguntas. Como a base não contém informações sobre clientes ou operações bancárias, os resultados descrevem apenas a amostra estudada."),
                html.P("Explore os gráficos, combine os filtros e consulte os registros para aprofundar a análise. A seta de cada gráfico abre uma interpretação dos resultados da seleção atual."),
                html.A("Conhecer a base Adult · UCI", href=SOURCE, target="_blank", rel="noopener noreferrer"),
            ]),
            html.H2("Leitura inicial da base completa · sem filtros", className="portfolio-section-title"),
            html.Div(className="socio-context-copy", children=[
                html.P("Os destaques a seguir descrevem os 32.561 registros da base completa, sem filtros ou exclusão de extremos. Permanecem fixos como referência, mesmo quando você altera a seleção dos gráficos."),
                html.Ul([html.Li(text) for text in base_findings(data)]),
                html.P("Os percentuais representam a proporção de pessoas em cada grupo, e não a distribuição do dinheiro total. As relações observadas são descritivas: não demonstram causa e efeito nem representam, necessariamente, a população atual."),
            ]),
        ]), id="socio-description-panel", is_open=False),
        dbc.Collapse(create_filters(data), id="socio-filters-panel", is_open=False),
        html.P("As cores identificam as mesmas faixas de renda em todos os gráficos. Use as setas para ver as leituras e passe o cursor para consultar os valores.", className="socio-chart-guide"),
        html.Div(className="socio-charts-grid", children=[
            create_chart_card("graph-renda", "COMPOSIÇÃO", "Pessoas por faixa de renda anual, em dólares", "fa-chart-pie", "socio-income-card"),
            create_chart_card("graph-genero", "COMPARAÇÃO ENTRE GRUPOS", "Quantidade por gênero e distribuição das faixas dentro de cada grupo", "fa-venus-mars", "socio-gender-card"),
            create_chart_card("graph-escolaridade", "FORMAÇÃO", "Todos os níveis de escolaridade por número de registros e faixa de renda", "fa-graduation-cap", "socio-education-card"),
            create_chart_card("graph-ocupacoes", "MERCADO DE TRABALHO", "As dez ocupações mais frequentes; traduções aproximadas das categorias da fonte", "fa-briefcase", "socio-occupation-card"),
            create_chart_card("graph-idade-renda", "DISTRIBUIÇÃO ETÁRIA", "Áreas empilhadas: cada cor é uma faixa de renda, e a borda superior é o total", "fa-chart-area", "socio-age-card"),
            create_chart_card("graph-horas-idade", "JORNADA SEMANAL", "Média por idade e renda; o cursor informa quantos registros sustentam cada ponto", "fa-clock", "socio-hours-card"),
        ]),
        html.Details(className="socio-dataset", children=[
            html.Summary("Consultar Base de Dados"),
            html.Div(className="socio-context-copy", children=[
                html.P("Esta tabela acompanha os mesmos filtros e a mesma exclusão IQR dos gráficos. A busca a seguir atua somente na tabela. O CSV inclui todos os resultados dessa busca, não apenas a página visível."),
                html.Div(className="socio-data-actions", children=[
                    html.Div([
                        html.Label("Pesquisar na tabela", htmlFor="socio-search", className="filter-label"),
                        dcc.Input(id="socio-search", type="search", placeholder="Buscar por escolaridade, ocupação ou outro valor…", value="", debounce=True),
                    ]),
                    html.Button("Baixar seleção em CSV", id="socio-export", n_clicks=0, type="button", className="project-link"),
                ]),
                html.P(id="socio-record-summary", className="socio-record-summary", **{"aria-live": "polite"}),
                dash_table.DataTable(
                    id="socio-records", columns=[{"name": title, "id": key,
                        "type": "numeric" if key in {"registro", "age", "hours_per_week", "education_num", "capital_gain", "capital_loss"} else "text"}
                        for key, title in TABLE_COLUMNS.items()],
                    data=[], page_action="custom", page_current=0, page_size=15, page_count=0,
                    sort_action="custom", sort_mode="multi", sort_by=[],
                    style_table={"overflowX": "auto"},
                    style_cell={"fontFamily": "Segoe UI, sans-serif", "fontSize": 12, "padding": "10px 12px", "textAlign": "left", "minWidth": "100px", "maxWidth": "260px", "whiteSpace": "normal", "height": "auto", "border": "1px solid #e9ebf2"},
                    style_header={"fontWeight": "600", "backgroundColor": "#f3f4f7"},
                    style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#fafbfc"}],
                ),
                html.P("O CSV usado pelo projeto preserva 14 colunas da fonte adaptada e não inclui o peso populacional fnlwgt. O identificador Registro corresponde à linha original do CSV. Os rótulos de ocupação, escolaridade e vínculo foram traduzidos para facilitar a leitura; outras categorias conservam os nomes originais.", className="socio-source-note"),
                html.A("Fonte e documentação · Adult (Census Income) · UCI", href=SOURCE, target="_blank", rel="noopener noreferrer"),
                dcc.Download(id="socio-download"),
            ]),
        ]),
    ])
