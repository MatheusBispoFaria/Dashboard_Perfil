"""Leitura, preparação e filtragem do conjunto de dados."""

from pathlib import Path

import pandas as pd

from .config import DATA_PATH


def load_dataset(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Carrega o CSV e prepara as colunas usadas pelo dashboard."""
    data = pd.read_csv(path)
    for column in ("income", "sex", "occupation"):
        data[column] = data[column].astype(str).str.strip()
    data["renda_alta"] = (data["income"] == ">50K").astype(int)

    for column in ("workclass", "education"):
        if column in data.columns:
            data[column] = data[column].astype(str).str.strip()
        else:
            data[column] = "N/A"
    return data


def filter_dataset(
    data,
    income=None,
    workclass=None,
    education=None,
    age=None,
    hours=None,
    sex=None,
):
    """Aplica os filtros sem modificar o conjunto de dados original."""
    filtered = data.copy()
    for column, values in (
        ("income", income),
        ("workclass", workclass),
        ("education", education),
        ("sex", sex),
    ):
        if values:
            filtered = filtered[filtered[column].isin(values)]
    for column, bounds in (("age", age), ("hours_per_week", hours)):
        if bounds:
            filtered = filtered[filtered[column].between(bounds[0], bounds[1])]
    return filtered


def calculate_iqr_bounds(data):
    """Limites fixos de Tukey na base original, nunca recalculados por filtro."""
    bounds = {}
    for column in ("age", "hours_per_week"):
        q1, q3 = data[column].quantile([0.25, 0.75])
        spread = q3 - q1
        # Uma variável constante não oferece dispersão para esta regra.
        if pd.notna(spread) and spread > 0:
            bounds[column] = (float(q1 - 1.5 * spread), float(q3 + 1.5 * spread))
    return bounds


def apply_iqr(data, bounds):
    mask = pd.Series(True, index=data.index)
    for column, (lower, upper) in bounds.items():
        mask &= data[column].between(lower, upper)
    return data.loc[mask].copy()


def select_dataset(data, income=None, workclass=None, education=None, age=None,
                   hours=None, sex=None, outliers=None, confidence="off"):
    """Um único recorte para gráficos, análises, tabela e download."""
    before = filter_dataset(data, income, workclass, education, age, hours, sex)
    selected = apply_iqr(before, calculate_iqr_bounds(data)) if "iqr" in (outliers or []) else before
    return selected, len(before) - len(selected), len(before)
