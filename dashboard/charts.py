"""Seis visualizações complementares da seleção socioeconômica."""

import textwrap
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .labels import EDUCATION, EDUCATION_ORDER, INCOME, OCCUPATION, SEX, label
from .socioeconomic import hours_summary, occupation_summary, wilson_interval
from .statistics import CONFIDENCE_Z
from .theme import C_BLUE, C_CYAN, LAYOUT_CLEAN

INCOME_COLORS = {"<=50K": C_BLUE, ">50K": C_CYAN}


def base_figure(height=300):
    fig = go.Figure()
    fig.update_layout(**LAYOUT_CLEAN, height=height, autosize=True)
    fig.update_layout(margin=dict(l=48, r=18, t=74, b=52),
                      legend=dict(orientation="h", x=0, y=1.02, yanchor="bottom", traceorder="normal", font_size=10),
                      hovermode="closest", separators=",.")
    return fig


def empty_figure(height=300):
    fig = base_figure(height)
    fig.add_annotation(text="Sem dados para esta seleção.", x=.5, y=.5,
                       xref="paper", yref="paper", showarrow=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def create_income_figure(data, confidence="off"):
    fig = base_figure(270)
    categories = [key for key in INCOME if data["income"].eq(key).any()]
    counts = [int(data["income"].eq(key).sum()) for key in categories]
    fig.add_trace(go.Pie(labels=[INCOME[key] for key in categories], values=counts,
                        marker_colors=[INCOME_COLORS[key] for key in categories], hole=.55,
                        sort=False, textinfo="percent", textfont_size=13,
                        hovertemplate="%{label}<br>Registros: %{value:,}<br>Participação na seleção: %{percent}<extra></extra>"))
    fig.update_layout(margin=dict(l=12, r=12, t=16, b=68),
                      legend=dict(orientation="h", x=.5, xanchor="center", y=-.06, yanchor="top"))
    if confidence != "off":
        lo, hi = wilson_interval(int(data["renda_alta"].sum()), len(data), CONFIDENCE_Z[confidence])
        fig.add_annotation(text=f"IC {confidence}% · renda >50K<br>{lo:.1f}% a {hi:.1f}%",
                           x=.5, y=.5, xref="paper", yref="paper", showarrow=False,
                           font=dict(size=10, color="#535d70"))
    return fig


def create_gender_figure(data, confidence="off"):
    fig = base_figure(270)
    groups = [value for value in SEX if data["sex"].eq(value).any()]
    totals = [int(data["sex"].eq(value).sum()) for value in groups]
    for income, color in INCOME_COLORS.items():
        counts = [int((data["sex"].eq(sex) & data["income"].eq(income)).sum()) for sex in groups]
        custom = []
        for sex, count, total in zip(groups, counts, totals):
            lo, hi = wilson_interval(count, total, CONFIDENCE_Z.get(confidence, 1.96))
            interval = f"IC {confidence}% (Wilson): {lo:.1f}% a {hi:.1f}%" if confidence != "off" else ""
            custom.append([total, count/total*100, total/len(data)*100, interval])
        fig.add_trace(go.Bar(name=INCOME[income], x=[SEX[value] for value in groups], y=counts,
                            marker_color=color, customdata=custom,
                            hovertemplate=("%{x}<br>%{fullData.name}<br>Registros: %{y:,}"
                                           "<br>Total do grupo: %{customdata[0]:,}"
                                           "<br>Faixa dentro do grupo: %{customdata[1]:.1f}%"
                                           "<br>Grupo na seleção: %{customdata[2]:.1f}%"
                                           "<br>%{customdata[3]}<extra></extra>")))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title="Registros")
    return fig


def _wrapped(text, width=24):
    return "<br>".join(textwrap.wrap(text, width=width))


def _count_bars(data, field, categories, mapping, height):
    fig = base_figure(height)
    for income, color in INCOME_COLORS.items():
        counts, custom = [], []
        for category in categories:
            group = data[data[field].eq(category)]
            count = int(group["income"].eq(income).sum())
            counts.append(count)
            custom.append([category, len(group), count/len(group)*100, float(group["age"].mean())])
        fig.add_trace(go.Bar(name=INCOME[income], x=counts,
                            y=[_wrapped(label(value, mapping)) for value in categories],
                            orientation="h", marker_color=color, customdata=custom,
                            hovertemplate=("%{y}<br>Categoria original: %{customdata[0]}"
                                           "<br>%{fullData.name}<br>Registros: %{x:,}"
                                           "<br>Total da categoria: %{customdata[1]:,}"
                                           "<br>Faixa dentro da categoria: %{customdata[2]:.1f}%"
                                           "<br>Idade média da categoria: %{customdata[3]:.1f} anos<extra></extra>")))
    fig.update_layout(barmode="stack", margin=dict(l=165, r=18, t=74, b=48))
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont_size=10)
    fig.update_xaxes(title="Registros", showgrid=True, gridcolor="#f0f1f7")
    return fig


def create_occupation_figure(data):
    categories = occupation_summary(data)["occupation"].tolist()
    if not categories:
        return empty_figure(410)
    return _count_bars(data, "occupation", categories, OCCUPATION, 410)


def create_education_figure(data):
    observed = set(data["education"])
    categories = [value for value in EDUCATION_ORDER if value in observed]
    categories += sorted(observed - set(categories))
    return _count_bars(data, "education", categories, EDUCATION, 490)


def create_age_income_figure(data):
    fig = base_figure(310)
    ages = list(range(int(data["age"].min()), int(data["age"].max()) + 1))
    for income, color in INCOME_COLORS.items():
        counts = data.loc[data["income"].eq(income)].groupby("age").size().reindex(ages, fill_value=0)
        fig.add_trace(go.Scatter(x=ages, y=counts, mode="lines", stackgroup="income",
                                name=INCOME[income], line=dict(color=color, width=1.7),
                                fillcolor=color,
                                hovertemplate="Idade: %{x} anos<br>%{fullData.name}<br>Registros: %{y:,}<extra></extra>"))
    fig.update_xaxes(title="Idade (anos)")
    fig.update_yaxes(title="Registros")
    return fig


def create_hours_age_figure(data, confidence="off"):
    fig = base_figure(310)
    summary = hours_summary(data)
    for income, color in INCOME_COLORS.items():
        group = summary.loc[summary["income"].eq(income)].sort_values("age")
        if group.empty:
            continue
        # Não liga dois pontos através de uma idade sem observações.
        ages = list(range(int(data["age"].min()), int(data["age"].max()) + 1))
        group = group.set_index("age").reindex(ages)
        counts = group["count"].fillna(0).astype(int)
        warnings = ["Grupo pequeno (menos de 5 registros)" if 0 < count < 5 else "" for count in counts]
        errors = None
        if confidence != "off":
            error = (CONFIDENCE_Z[confidence] * group["std"] / group["count"].pow(.5))
            errors = dict(type="data", array=error.where(group["count"].ge(2), np.nan), visible=True)
        fig.add_trace(go.Scatter(x=ages, y=group["mean"], mode="lines+markers", connectgaps=False,
                                name=INCOME[income], line=dict(color=color, width=2),
                                marker=dict(color=color, size=[7 if 0<count<5 else 4 for count in counts],
                                            symbol=["circle-open" if 0<count<5 else "circle" for count in counts]),
                                customdata=list(zip(counts, warnings)), error_y=errors,
                                hovertemplate=("Idade: %{x} anos<br>%{fullData.name}"
                                               "<br>Média: %{y:.1f} h/semana"
                                               "<br>Registros nesta idade e renda: %{customdata[0]}"
                                               "<br>%{customdata[1]}<extra></extra>")))
    fig.update_xaxes(title="Idade (anos)")
    fig.update_yaxes(title="Média de horas/semana", rangemode="tozero")
    return fig


def create_dashboard_figures(data, confidence="off"):
    builders = {
        "graph-renda": lambda: create_income_figure(data, confidence),
        "graph-genero": lambda: create_gender_figure(data, confidence),
        "graph-escolaridade": lambda: create_education_figure(data),
        "graph-ocupacoes": lambda: create_occupation_figure(data),
        "graph-idade-renda": lambda: create_age_income_figure(data),
        "graph-horas-idade": lambda: create_hours_age_figure(data, confidence),
    }
    return {key: empty_figure() if data.empty else builder() for key, builder in builders.items()}
