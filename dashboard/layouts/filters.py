"""Filtros da análise de dados."""

from dash import dcc, html
import dash_bootstrap_components as dbc


def create_filters(data):
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Renda", className="card-title-sm"),
                    dcc.Dropdown(
                        id="filtro-renda",
                        options=[{"label": i, "value": i} for i in data["income"].unique()],
                        multi=True,
                        placeholder="Todas"
                    )
                ], width=2),
                dbc.Col([
                    html.Label("Vínculo", className="card-title-sm"),
                    dcc.Dropdown(
                        id="filtro-vinculo",
                        options=[{"label": i, "value": i} for i in data["workclass"].unique() if i != 'nan'],
                        multi=True,
                        placeholder="Todos"
                    )
                ], width=2),
                dbc.Col([
                    html.Label("Escolaridade", className="card-title-sm"),
                    dcc.Dropdown(
                        id="filtro-escolaridade",
                        options=[{"label": i, "value": i} for i in data["education"].unique() if i != 'nan'],
                        multi=True,
                        placeholder="Todas"
                    )
                ], width=2),
                dbc.Col([
                    html.Label("Idade", className="card-title-sm"),
                    dcc.RangeSlider(
                        id="filtro-idade",
                        min=data["age"].min(), max=data["age"].max(),
                        value=[data["age"].min(), data["age"].max()],
                        marks=None, tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=3),
                dbc.Col([
                    html.Label("Jornada (Horas)", className="card-title-sm"),
                    dcc.RangeSlider(
                        id="filtro-jornada",
                        min=data["hours_per_week"].min(), max=data["hours_per_week"].max(),
                        value=[data["hours_per_week"].min(), data["hours_per_week"].max()],
                        marks=None, tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=3),
            ], className="align-items-center"),
            dbc.Row([
                dbc.Col([
                    html.Label("Intervalo de Confiança", className="card-title-sm"),
                    dcc.Dropdown(
                        id="filtro-ic",
                        options=[
                            {"label": "Desativado", "value": "off"},
                            {"label": "90%", "value": "90"},
                            {"label": "95%", "value": "95"},
                            {"label": "99%", "value": "99"},
                        ],
                        value="off",
                        clearable=False
                    )
                ], width=3)
            ], className="mt-3")
        ]),
        className="mb-4 dash-card", style={"padding": "10px"}
    )
