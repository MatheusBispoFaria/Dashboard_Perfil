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
                html.P("Este estudo fez parte de um checkpoint que compôs minha avaliação em 2026. A proposta era construir um dashboard profissional com minha apresentação, qualificações e experiências, tendo como foco uma análise de dados sobre um tema de interesse."),
                html.P("Por recomendação do professor, escolhi a base Adult, também conhecida como Census Income, disponibilizada pelo repositório UCI. Ela reúne informações socioeconômicas dos Estados Unidos de 1994 e foi publicada em 1996; não é uma série histórica de 1994 a 1996. Utilizei 32.561 registros para explorar as relações entre renda, escolaridade, idade, ocupação e jornada de trabalho."),
                html.P("Meu objetivo era exercitar a leitura de perfis socioeconômicos em um contexto de interesse pelo setor bancário, aplicando meus conhecimentos de interpretação de gráficos e construção de dashboards. A base não identifica clientes nem contém informações de relacionamento bancário ou crédito: as conclusões se limitam à amostra e às associações observadas."),
                html.P("A análise abaixo permite formular perguntas, comparar grupos e examinar os registros. Cada seta abre uma interpretação do gráfico, com os resultados da seleção atual."),
                html.A("Conhecer a base Adult · UCI", href=SOURCE, target="_blank", rel="noopener noreferrer"),
            ]),
            html.H2("Leitura inicial da base completa · sem filtros", className="portfolio-section-title"),
            html.Div(className="socio-context-copy", children=[
                html.P("Estes números descrevem os registros originais, antes de qualquer filtro e da exclusão de extremos. Eles servem de referência e não são recalculados pela seleção abaixo."),
                html.Ul([html.Li(text) for text in base_findings(data)]),
                html.P("Os percentuais contam pessoas, e não valores monetários. As comparações entre escolaridade, ocupação e renda são descritivas: não demonstram causalidade nem permitem generalizar os resultados para a população atual."),
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
