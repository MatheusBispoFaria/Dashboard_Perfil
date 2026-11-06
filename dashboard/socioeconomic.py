"""Agregações e consulta paginada da amostra socioeconômica."""

import math
import pandas as pd

from .labels import EDUCATION, INCOME, OCCUPATION, SEX, WORKCLASS, label


def occupation_summary(data):
    valid = data.loc[~data["occupation"].isin(["nan", "N/A", "?", ""])]
    return (valid.groupby("occupation").agg(count=("age", "size"), mean_age=("age", "mean"))
            .sort_values(["count", "occupation"], ascending=[False, True]).head(10).reset_index())


def hours_summary(data):
    return (data.groupby(["age", "income"])["hours_per_week"]
            .agg(["mean", "std", "count"]).reset_index())


def wilson_interval(successes, total, z):
    if not total:
        return None, None
    rate = successes / total
    denominator = 1 + z*z/total
    center = (rate + z*z/(2*total)) / denominator
    margin = z * math.sqrt(rate*(1-rate)/total + z*z/(4*total*total)) / denominator
    return max(0, (center-margin)*100), min(100, (center+margin)*100)


TABLE_COLUMNS = {
    "registro": "Registro", "age": "Idade", "sex": "Gênero (sexo na fonte)",
    "income": "Renda anual", "education": "Escolaridade", "occupation": "Ocupação",
    "hours_per_week": "Horas/semana", "workclass": "Vínculo", "education_num": "Nível escolar (código)",
    "marital_status": "Estado civil (original)", "relationship": "Relação familiar (original)",
    "race": "Raça (original)", "capital_gain": "Ganho de capital (US$)",
    "capital_loss": "Perda de capital (US$)", "native_country": "País de origem (original)",
}


def displayed_records(data):
    result = data.drop(columns=["renda_alta"], errors="ignore").copy()
    result.insert(0, "registro", data.index + 1)
    for column, mapping in (("sex", SEX), ("income", INCOME), ("education", EDUCATION),
                            ("occupation", OCCUPATION), ("workclass", WORKCLASS)):
        result[column] = result[column].map(lambda value: label(value, mapping))
    return result[[column for column in TABLE_COLUMNS if column in result]]


def query_records(data, search=None, sort_by=None):
    result = displayed_records(data)
    query = str(search or "").strip()
    if query:
        mask = pd.Series(False, index=result.index)
        for column in result:
            mask |= result[column].astype(str).str.contains(query, case=False, regex=False, na=False)
        result = result.loc[mask]
    sort_by = [item for item in (sort_by or []) if item.get("column_id") in result]
    if sort_by:
        result = result.sort_values([item["column_id"] for item in sort_by],
                                    ascending=[item.get("direction") != "desc" for item in sort_by],
                                    kind="stable")
    return result
