"""Leitura do recorte preparado com o tratamento do CP5 original."""

from functools import lru_cache
import json

import pandas as pd

from ..config import PROJECT_ROOT

DATA_DIRECTORY = PROJECT_ROOT / "data" / "despesas_es"
AREAS = ("URBANISMO", "TRANSPORTE", "HABITAÇÃO", "SANEAMENTO", "GESTÃO AMBIENTAL")
VALUES = ("ValorEmpenho", "ValorLiquidado", "ValorPago", "ValorRap")
TEXT_COLUMNS = ("Funcao", "Subtitulo", "SubFuncao", "Programa", "Acao", "UnidadeGestora")
TRACE_COLUMNS = ("Id", "Ano", "Data", *TEXT_COLUMNS, *VALUES)


@lru_cache(maxsize=1)
def load_provenance():
    return json.loads((DATA_DIRECTORY / "proveniencia.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_data():
    return pd.read_csv(
        DATA_DIRECTORY / "despesas_es_2024_2025.csv.gz",
        dtype={"Id": "string", "Ano": "Int64", **{name: "string" for name in TEXT_COLUMNS}},
        parse_dates=["Data"],
        float_precision="round_trip",
    )


def filter_data(area="ALL", years=None, start=None, end=None, locations=None,
                subfunctions=None, programs=None, units=None):
    data = load_data()
    mask = pd.Series(True, index=data.index)
    if area and area != "ALL":
        mask &= data["Funcao"].eq(area)
    if years:
        mask &= data["Ano"].isin([int(year) for year in years])
    if start:
        mask &= data["Data"].ge(pd.to_datetime(start))
    if end:
        mask &= data["Data"].le(pd.to_datetime(end))
    for column, values in (
        ("Subtitulo", locations), ("SubFuncao", subfunctions),
        ("Programa", programs), ("UnidadeGestora", units),
    ):
        if values:
            mask &= data[column].isin(values)
    return data.loc[mask].copy()


def filter_options(area):
    data = load_data()
    if area and area != "ALL":
        data = data[data["Funcao"].eq(area)]
    return [
        [{"label": value, "value": value} for value in sorted(data[column].dropna().unique())]
        for column in ("Subtitulo", "SubFuncao", "Programa", "UnidadeGestora")
    ]


def trace_records(data, page, page_size, sort_by):
    """Paginação no servidor: somente a página atual vai para o navegador."""
    if sort_by:
        valid = [item for item in sort_by if item["column_id"] in TRACE_COLUMNS]
        if valid:
            data = data.sort_values(
                [item["column_id"] for item in valid],
                ascending=[item["direction"] == "asc" for item in valid],
                kind="stable",
            )
    table = data.iloc[page * page_size:(page + 1) * page_size][list(TRACE_COLUMNS)].copy()
    table["Data"] = table["Data"].dt.strftime("%d/%m/%Y")
    table[list(VALUES)] = table[list(VALUES)].round(2)
    return table.astype(object).where(pd.notna(table), None).to_dict("records")
