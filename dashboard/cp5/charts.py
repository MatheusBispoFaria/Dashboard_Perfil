from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .analytics import pearson_diario, serie_diaria


TEMPLATE = "plotly_white"

CONFIG = {
    "displaylogo": False,
    "responsive": True,
}

EMPENHADO_COR = "#173F5F"
LIQUIDADO_COR = "#20639B"
PAGO_COR = "#3CAEA3"
AZUL = "#0b4f8a"
AZUL_MEDIO = LIQUIDADO_COR
AZUL_CLARO = PAGO_COR
PRETO = "#111111"
CINZA_TEXTO = "#4f4f4f"
CINZA_GRID = "#e8e8e8"
CINZA_EIXO = "#cfcfcf"
FONT_FAMILY = "Segoe UI, Arial, sans-serif"


def vazio(titulo: str, mensagem: str = "Nenhum dado para os filtros selecionados") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=mensagem,
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 13, "family": FONT_FAMILY, "color": CINZA_TEXTO},
    )
    fig.update_layout(
        title={
            "text": titulo,
            "x": 0.01,
            "xanchor": "left",
            "font": {"size": 15, "family": FONT_FAMILY, "color": PRETO},
        },
        template=TEMPLATE,
        margin=dict(l=30, r=20, t=50, b=30),
        height=290,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={"family": FONT_FAMILY, "size": 12, "color": PRETO},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def _base(fig: go.Figure, titulo: str, height: int = 290) -> go.Figure:
    fig.update_layout(
        title={
            "text": titulo,
            "x": 0.01,
            "xanchor": "left",
            "font": {"size": 15, "family": FONT_FAMILY, "color": PRETO},
        },
        template=TEMPLATE,
        height=height,
        margin=dict(l=42, r=18, t=52, b=38),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={"family": FONT_FAMILY, "size": 12, "color": PRETO},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            font=dict(family=FONT_FAMILY, size=11, color=PRETO),
        ),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor=CINZA_EIXO,
            font=dict(family=FONT_FAMILY, size=12, color=PRETO),
        ),
    )

    fig.update_xaxes(
        gridcolor=CINZA_GRID,
        linecolor=CINZA_EIXO,
        zerolinecolor=CINZA_EIXO,
        tickfont=dict(family=FONT_FAMILY, size=11, color=PRETO),
        title_font=dict(family=FONT_FAMILY, size=12, color=PRETO),
    )
    fig.update_yaxes(
        gridcolor=CINZA_GRID,
        linecolor=CINZA_EIXO,
        zerolinecolor=CINZA_EIXO,
        tickfont=dict(family=FONT_FAMILY, size=11, color=PRETO),
        title_font=dict(family=FONT_FAMILY, size=12, color=PRETO),
    )
    return fig


def evolucao(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return vazio("Evolução financeira")

    diario = serie_diaria(df)
    intervalo = (diario["Data"].max() - diario["Data"].min()).days if len(diario) else 0

    if intervalo > 70:
        diario["Periodo"] = diario["Data"].dt.to_period("M").dt.to_timestamp()
        dados = diario.groupby("Periodo", as_index=False)[
            ["ValorEmpenho", "ValorLiquidado", "ValorPago"]
        ].sum()
        x = "Periodo"
    else:
        dados = diario.rename(columns={"Data": "Periodo"})
        x = "Periodo"

    fig = go.Figure()
    cores = {
        "ValorEmpenho": EMPENHADO_COR,
        "ValorLiquidado": LIQUIDADO_COR,
        "ValorPago": PAGO_COR,
    }

    for coluna, nome in [
        ("ValorEmpenho", "Empenhado"),
        ("ValorLiquidado", "Liquidado"),
        ("ValorPago", "Pago"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=dados[x],
                y=dados[coluna],
                mode="lines+markers",
                name=nome,
                line=dict(color=cores[coluna], width=2),
                marker=dict(color=cores[coluna], size=5),
            )
        )

    fig.update_yaxes(tickprefix="R$ ", tickformat="~s")
    return _base(fig, "Evolução financeira")


def por_regiao(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return vazio("Pago por localizador territorial")

    dados = (
        df.assign(Subtitulo=df["Subtitulo"].fillna("Não informado"))
        .groupby("Subtitulo", as_index=False)["ValorPago"]
        .sum()
        .sort_values("ValorPago", ascending=True)
    )

    fig = px.bar(dados, x="ValorPago", y="Subtitulo", orientation="h")
    fig.update_traces(marker_color=AZUL)
    fig.update_xaxes(tickprefix="R$ ", tickformat="~s", title=None)
    fig.update_yaxes(title=None)
    return _base(fig, "Pago por localizador territorial")


def programas(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return vazio("Principais programas")

    dados = (
        df.assign(Programa=df["Programa"].fillna("Não informado"))
        .groupby("Programa", as_index=False)["ValorPago"]
        .sum()
        .nlargest(8, "ValorPago")
        .sort_values("ValorPago", ascending=True)
    )

    fig = px.bar(dados, x="ValorPago", y="Programa", orientation="h")
    fig.update_traces(marker_color=AZUL)
    fig.update_xaxes(tickprefix="R$ ", tickformat="~s", title=None)
    fig.update_yaxes(title=None)
    return _base(fig, "Principais programas")


def execucao_subfuncao(df: pd.DataFrame) -> go.Figure:
    """
    Compara os estágios financeiros por subfunção.

    A antiga razão Pago/Empenho foi removida para evitar tratar movimentos
    financeiros do período como um percentual contábil de execução.
    """
    if df.empty:
        return vazio("Estágios financeiros por subfunção")

    dados = (
        df.assign(SubFuncao=df["SubFuncao"].fillna("Não informado"))
        .groupby("SubFuncao", as_index=False)[
            ["ValorEmpenho", "ValorLiquidado", "ValorPago"]
        ]
        .sum()
    )

    if dados.empty:
        return vazio("Estágios financeiros por subfunção")

    # Limita a leitura visual às subfunções mais relevantes pelo valor pago.
    top = dados.nlargest(8, "ValorPago")["SubFuncao"]
    dados = dados[dados["SubFuncao"].isin(top)].copy()

    longo = dados.melt(
        id_vars="SubFuncao",
        value_vars=["ValorEmpenho", "ValorLiquidado", "ValorPago"],
        var_name="Medida",
        value_name="Valor",
    )
    longo["Medida"] = longo["Medida"].map(
        {
            "ValorEmpenho": "Empenhado",
            "ValorLiquidado": "Liquidado",
            "ValorPago": "Pago",
        }
    )

    ordem = dados.sort_values("ValorPago", ascending=True)["SubFuncao"].tolist()

    fig = px.bar(
        longo,
        x="Valor",
        y="SubFuncao",
        color="Medida",
        orientation="h",
        barmode="group",
        category_orders={"SubFuncao": ordem},
        color_discrete_map={
            "Empenhado": EMPENHADO_COR,
            "Liquidado": LIQUIDADO_COR,
            "Pago": PAGO_COR,
        },
    )
    fig.update_xaxes(tickprefix="R$ ", tickformat="~s", title=None)
    fig.update_yaxes(title=None)
    return _base(fig, "Estágios financeiros por subfunção")


def boxplot_regiao(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return vazio("Dispersão diária por localizador territorial")

    base = df.dropna(subset=["Data"]).copy()
    base["Subtitulo"] = base["Subtitulo"].fillna("Não informado")

    dados = (
        base.groupby(["Data", "Subtitulo"], as_index=False)["ValorPago"]
        .sum()
    )

    fig = px.box(dados, x="Subtitulo", y="ValorPago", points="outliers")
    fig.update_traces(marker_color=AZUL, line_color=AZUL, fillcolor=AZUL_CLARO)
    fig.update_yaxes(tickprefix="R$ ", tickformat="~s", title=None)
    fig.update_xaxes(title=None)
    return _base(fig, "Boxplot do valor pago diário por localizador", 310)


def histograma(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return vazio("Distribuição dos pagamentos")

    dados = df.loc[df["ValorPago"] != 0, ["ValorPago"]].dropna().copy()
    if dados.empty:
        return vazio("Distribuição dos pagamentos", "Não há valores pagos diferentes de zero")

    fig = px.histogram(dados, x="ValorPago", nbins=45)
    fig.update_traces(
        marker_color=AZUL,
        marker_line_color="#ffffff",
        marker_line_width=0.5,
    )
    fig.update_xaxes(tickprefix="R$ ", tickformat="~s", title=None)
    fig.update_yaxes(title="Registros")
    return _base(fig, "Histograma dos valores pagos por registro", 310)


def corrplot(df: pd.DataFrame) -> go.Figure:
    diario = serie_diaria(df)
    if len(diario) < 3:
        return vazio("Correlação entre medidas financeiras")

    colunas = ["ValorEmpenho", "ValorLiquidado", "ValorPago", "ValorRap"]
    corr = diario[colunas].corr()
    nomes = ["Empenho", "Liquidado", "Pago", "RAP"]

    fig = px.imshow(
        corr,
        x=nomes,
        y=nomes,
        zmin=-1,
        zmax=1,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
    )
    fig.update_layout(coloraxis_colorbar=dict(title="r"))
    return _base(fig, "Corrplot diário", 310)


def pearson_scatter(df: pd.DataFrame) -> tuple[go.Figure, dict]:
    diario = serie_diaria(df)
    info = pearson_diario(df)

    if len(diario) < 3:
        return vazio("Empenhado × pago"), info

    fig = px.scatter(
        diario,
        x="ValorEmpenho",
        y="ValorPago",
        hover_data={"Data": True},
    )
    fig.update_traces(marker=dict(color=AZUL, size=7, opacity=0.75))

    x = diario["ValorEmpenho"].to_numpy(dtype=float)
    y = diario["ValorPago"].to_numpy(dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)

    if mask.sum() >= 2 and np.unique(x[mask]).size >= 2:
        m, b = np.polyfit(x[mask], y[mask], 1)
        ordem = np.argsort(x[mask])
        xx = x[mask][ordem]
        fig.add_trace(
            go.Scatter(
                x=xx,
                y=m * xx + b,
                mode="lines",
                name="Tendência linear",
                line=dict(color=PRETO, width=2),
            )
        )

    fig.update_xaxes(tickprefix="R$ ", tickformat="~s", title="Empenhado por dia")
    fig.update_yaxes(tickprefix="R$ ", tickformat="~s", title="Pago por dia")
    return _base(fig, "Correlação de Pearson — empenhado × pago", 310), info
