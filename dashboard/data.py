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
):
    """Aplica os filtros sem modificar o conjunto de dados original."""
    filtered = data.copy()
    for column, values in (
        ("income", income),
        ("workclass", workclass),
        ("education", education),
    ):
        if values:
            filtered = filtered[filtered[column].isin(values)]
    for column, bounds in (("age", age), ("hours_per_week", hours)):
        if bounds:
            filtered = filtered[filtered[column].between(bounds[0], bounds[1])]
    return filtered
