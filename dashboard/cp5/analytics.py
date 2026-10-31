from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

VALORES = ["ValorEmpenho", "ValorLiquidado", "ValorPago", "ValorRap"]


def moeda(valor: float | int | None) -> str:
    if valor is None or pd.isna(valor):
        return "R$ 0,00"

    valor = float(valor)
    sinal = "-" if valor < 0 else ""
    valor = abs(valor)

    if valor >= 1_000_000_000:
        return f"{sinal}R$ {valor / 1_000_000_000:.2f} bi".replace(".", ",")
    if valor >= 1_000_000:
        return f"{sinal}R$ {valor / 1_000_000:.2f} mi".replace(".", ",")
    if valor >= 1_000:
        return f"{sinal}R$ {valor / 1_000:.1f} mil".replace(".", ",")

    return f"{sinal}R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def percentual(valor: float | None) -> str:
    if valor is None or pd.isna(valor) or not math.isfinite(valor):
        return "—"
    return f"{valor:.1f}%".replace(".", ",")


def kpis(df: pd.DataFrame) -> dict:
    """
    Retorna os quatro estágios monetários sem derivar uma razão de execução.

    A relação simples Pago/Empenho foi removida porque os registros contêm
    movimentos, ajustes e valores negativos; somas do mesmo recorte podem gerar
    razões superiores a 100% ou negativas e induzir uma interpretação contábil
    incorreta.
    """
    if df.empty:
        return {"empenho": 0.0, "liquidado": 0.0, "pago": 0.0, "rap": 0.0}

    totais = df[VALORES].sum(numeric_only=True)

    return {
        "empenho": float(totais.get("ValorEmpenho", 0.0)),
        "liquidado": float(totais.get("ValorLiquidado", 0.0)),
        "pago": float(totais.get("ValorPago", 0.0)),
        "rap": float(totais.get("ValorRap", 0.0)),
    }


def serie_diaria(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Data", *VALORES])

    return (
        df.dropna(subset=["Data"])
        .groupby("Data", as_index=False)[VALORES]
        .sum()
        .sort_values("Data")
    )


def intervalo_confianca_media_diaria(df: pd.DataFrame, confianca: float = 0.95) -> dict:
    diario = serie_diaria(df)
    valores = diario["ValorPago"].dropna().astype(float)
    n = len(valores)

    if n < 2:
        return {"media": np.nan, "inferior": np.nan, "superior": np.nan, "n": n}

    media = float(valores.mean())
    desvio = float(valores.std(ddof=1))

    if desvio == 0:
        return {"media": media, "inferior": media, "superior": media, "n": n}

    erro = stats.sem(valores, nan_policy="omit")
    critico = stats.t.ppf((1 + confianca) / 2, df=n - 1)
    margem = float(critico * erro)

    return {
        "media": media,
        "inferior": media - margem,
        "superior": media + margem,
        "n": n,
    }


def dispersao_diaria(df: pd.DataFrame) -> dict:
    valores = serie_diaria(df)["ValorPago"].dropna().astype(float)

    if valores.empty:
        return {"media": np.nan, "mediana": np.nan, "desvio": np.nan, "cv": np.nan}

    media = float(valores.mean())
    desvio = float(valores.std(ddof=1)) if len(valores) > 1 else 0.0
    cv = (desvio / abs(media) * 100) if media != 0 else np.nan

    return {
        "media": media,
        "mediana": float(valores.median()),
        "desvio": desvio,
        "cv": cv,
    }


def pearson_diario(df: pd.DataFrame) -> dict:
    diario = serie_diaria(df)
    pares = diario[["ValorEmpenho", "ValorPago"]].dropna()

    if len(pares) < 3 or pares["ValorEmpenho"].nunique() < 2 or pares["ValorPago"].nunique() < 2:
        return {"r": np.nan, "p": np.nan, "n": len(pares)}

    r, p = stats.pearsonr(pares["ValorEmpenho"], pares["ValorPago"])
    return {"r": float(r), "p": float(p), "n": len(pares)}
