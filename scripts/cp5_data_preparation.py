from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
ANOS_ANALISADOS = [2024, 2025]

AREAS_MONITORADAS = [
    "URBANISMO",
    "TRANSPORTE",
    "HABITAÇÃO",
    "SANEAMENTO",
    "GESTÃO AMBIENTAL",
]

# Colunas mantidas depois da preparação.
COLUNAS_ANALISE = [
    "Id",
    "Ano",
    "Data",
    "ValorEmpenho",
    "ValorLiquidado",
    "ValorPago",
    "ValorRap",
    "Funcao",
    "Subtitulo",
    "SubFuncao",
    "Programa",
    "Acao",
    "UnidadeGestora",
]

# Os códigos são lidos porque em 2025 vários rótulos textuais vieram vazios.
# Eles permitem reconstruir as descrições usando as relações código -> rótulo
# observadas na própria base oficial de 2024.
COLUNAS_ORIGEM = [
    *COLUNAS_ANALISE,
    "CodigoFuncao",
    "CodigoSubFuncao",
    "CodigoPrograma",
    "CodigoAcao",
    "CodigoSubtitulo",
]

VALORES = ["ValorEmpenho", "ValorLiquidado", "ValorPago", "ValorRap"]
TEXTOS = ["Funcao", "Subtitulo", "SubFuncao", "Programa", "Acao", "UnidadeGestora"]

COLUNAS_RASTREABILIDADE = [
    "Id",
    "Ano",
    "Data",
    "SubFuncao",
    "Programa",
    "Acao",
    "Subtitulo",
    "UnidadeGestora",
    "ValorEmpenho",
    "ValorLiquidado",
    "ValorPago",
    "ValorRap",
]


def _arquivos_ano(ano: int) -> list[Path]:
    padrao = f"despesas_es_{ano}_completo_parte_*.zip"
    arquivos = sorted(RAW_DIR.glob(padrao))
    if len(arquivos) == 4:
        return arquivos

    # Também aceita os ZIPs diretamente na raiz do projeto.
    return sorted(BASE_DIR.glob(padrao))


def arquivos_dados() -> dict[int, list[Path]]:
    """Localiza as quatro partes de 2024 e as quatro partes de 2025."""
    return {ano: _arquivos_ano(ano) for ano in ANOS_ANALISADOS}


def dados_disponiveis() -> bool:
    arquivos = arquivos_dados()
    return all(len(arquivos[ano]) == 4 for ano in ANOS_ANALISADOS)


def _texto_vazio(serie: pd.Series) -> pd.Series:
    texto = serie.astype("string").str.strip()
    return texto.isna() | texto.eq("")


def _moeda_para_float(serie: pd.Series) -> pd.Series:
    """
    Converte o formato monetário da fonte para número.

    Valores inválidos permanecem como NaN para que possam ser auditados;
    eles não são transformados silenciosamente em zero.
    """
    return pd.to_numeric(
        serie.astype("string")
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )


def _adicionar_mapa_simples(
    destino: dict[str, str],
    bruto: pd.DataFrame,
    codigo: str,
    rotulo: str,
) -> None:
    pares = bruto[[codigo, rotulo]].copy()
    pares[codigo] = pares[codigo].astype("string").str.strip()
    pares[rotulo] = pares[rotulo].astype("string").str.strip()
    pares = pares[
        pares[codigo].notna()
        & pares[codigo].ne("")
        & pares[rotulo].notna()
        & pares[rotulo].ne("")
    ].drop_duplicates()

    for cod, nome in pares.itertuples(index=False, name=None):
        destino.setdefault(str(cod), str(nome))


def _atualizar_mapas_2024(bruto: pd.DataFrame, mapas: dict) -> None:
    """Acumula relações oficiais código -> descrição observadas em 2024."""
    _adicionar_mapa_simples(mapas["funcao"], bruto, "CodigoFuncao", "Funcao")
    _adicionar_mapa_simples(mapas["subfuncao"], bruto, "CodigoSubFuncao", "SubFuncao")
    _adicionar_mapa_simples(mapas["subtitulo"], bruto, "CodigoSubtitulo", "Subtitulo")

    programas = bruto[["CodigoFuncao", "CodigoPrograma", "Programa"]].copy()
    for coluna in programas.columns:
        programas[coluna] = programas[coluna].astype("string").str.strip()
    programas = programas[
        programas["CodigoFuncao"].notna()
        & programas["CodigoFuncao"].ne("")
        & programas["CodigoPrograma"].notna()
        & programas["CodigoPrograma"].ne("")
        & programas["Programa"].notna()
        & programas["Programa"].ne("")
    ].drop_duplicates()

    for cod_funcao, cod_programa, nome in programas.itertuples(index=False, name=None):
        chave = (str(cod_funcao), str(cod_programa))
        mapas["programa_contexto"].setdefault(chave, str(nome))
        mapas["programa_global_sets"].setdefault(str(cod_programa), set()).add(str(nome))


def _finalizar_mapas(mapas: dict) -> None:
    mapas["programa_global"] = {
        codigo: next(iter(nomes))
        for codigo, nomes in mapas["programa_global_sets"].items()
        if len(nomes) == 1
    }


def _preencher_por_codigo(
    chunk: pd.DataFrame,
    rotulo: str,
    codigo: str,
    mapa: dict[str, str],
    prefixo_fallback: str,
) -> tuple[pd.Series, int, int]:
    atual = chunk[rotulo].astype("string").str.strip()
    codigos = chunk[codigo].astype("string").str.strip()
    vazio = atual.isna() | atual.eq("")

    mapeado = codigos.map(mapa)
    reconstruido = vazio & mapeado.notna()
    atual = atual.mask(reconstruido, mapeado)

    fallback = vazio & atual.isna() & codigos.notna() & codigos.ne("")
    atual = atual.mask(fallback, prefixo_fallback + " " + codigos)

    return atual, int(reconstruido.sum()), int(fallback.sum())


def _normalizar_chunk(
    bruto: pd.DataFrame,
    ano: int,
    mapas: dict,
) -> tuple[pd.DataFrame, dict[str, int], dict[str, int]]:
    chunk = bruto.copy()

    chunk["Id"] = chunk["Id"].astype("string").str.strip()
    chunk["Ano"] = pd.to_numeric(chunk["Ano"], errors="coerce").fillna(ano).astype("Int64")

    for coluna in [*TEXTOS, "CodigoFuncao", "CodigoSubFuncao", "CodigoPrograma", "CodigoAcao", "CodigoSubtitulo"]:
        chunk[coluna] = chunk[coluna].astype("string").str.strip()

    reconstruidos = {"Funcao": 0, "SubFuncao": 0, "Programa": 0, "Subtitulo": 0}
    fallbacks = {"Funcao": 0, "SubFuncao": 0, "Programa": 0, "Subtitulo": 0}

    # Em 2025 os rótulos abaixo vieram vazios na fonte. Reconstruímos apenas
    # quando existe uma correspondência observada nos dados oficiais de 2024.
    if ano == 2025:
        chunk["Funcao"], reconstruidos["Funcao"], fallbacks["Funcao"] = _preencher_por_codigo(
            chunk, "Funcao", "CodigoFuncao", mapas["funcao"], "FUNÇÃO"
        )
        chunk["SubFuncao"], reconstruidos["SubFuncao"], fallbacks["SubFuncao"] = _preencher_por_codigo(
            chunk, "SubFuncao", "CodigoSubFuncao", mapas["subfuncao"], "SUBFUNÇÃO"
        )
        chunk["Subtitulo"], reconstruidos["Subtitulo"], fallbacks["Subtitulo"] = _preencher_por_codigo(
            chunk, "Subtitulo", "CodigoSubtitulo", mapas["subtitulo"], "LOCALIZADOR"
        )

        programa_atual = chunk["Programa"].astype("string").str.strip()
        cod_funcao = chunk["CodigoFuncao"].astype("string").str.strip()
        cod_programa = chunk["CodigoPrograma"].astype("string").str.strip()
        vazio_programa = programa_atual.isna() | programa_atual.eq("")

        contexto = pd.Series(
            [mapas["programa_contexto"].get((str(f), str(p))) for f, p in zip(cod_funcao, cod_programa)],
            index=chunk.index,
            dtype="string",
        )
        global_unico = cod_programa.map(mapas.get("programa_global", {})).astype("string")
        candidato = contexto.fillna(global_unico)

        reconstruido = vazio_programa & candidato.notna()
        programa_atual = programa_atual.mask(reconstruido, candidato)
        fallback = vazio_programa & programa_atual.isna() & cod_programa.notna() & cod_programa.ne("")
        programa_atual = programa_atual.mask(fallback, "PROGRAMA " + cod_programa)

        chunk["Programa"] = programa_atual
        reconstruidos["Programa"] = int(reconstruido.sum())
        fallbacks["Programa"] = int(fallback.sum())

    chunk["Funcao"] = chunk["Funcao"].str.upper()
    chunk["Data"] = pd.to_datetime(chunk["Data"], dayfirst=True, errors="coerce")

    for coluna in VALORES:
        chunk[coluna] = _moeda_para_float(chunk[coluna])

    # Ação e unidade gestora estão preenchidas em 2025; se um registro futuro
    # vier sem descrição da ação, o código é exibido de forma transparente.
    acao_vazia = _texto_vazio(chunk["Acao"])
    codigo_acao = chunk["CodigoAcao"].astype("string").str.strip()
    chunk.loc[acao_vazia & codigo_acao.notna() & codigo_acao.ne(""), "Acao"] = (
        "AÇÃO " + codigo_acao[acao_vazia & codigo_acao.notna() & codigo_acao.ne("")]
    )

    return chunk[COLUNAS_ANALISE], reconstruidos, fallbacks


@lru_cache(maxsize=1)
def _carregar_base_e_auditoria() -> tuple[pd.DataFrame, dict]:
    """
    Lê as bases integrais de 2024 e 2025 em blocos e mantém em memória
    somente o recorte temático usado pela POC.

    Em 2025, Funcao/SubFuncao/Programa/Subtitulo chegam sem descrição textual.
    A preparação reconstrói esses rótulos a partir dos códigos oficiais usando
    as correspondências observadas em 2024 e registra quantos casos precisaram
    de fallback quando não havia correspondência segura.
    """
    arquivos_por_ano = arquivos_dados()
    if not dados_disponiveis():
        auditoria_vazia = {
            "registros_base_integral": 0,
            "registros_recorte": 0,
            "registros_base_integral_por_ano": {},
            "registros_recorte_por_ano": {},
            "duplicados_id_base_integral": 0,
            "datas_invalidas_base_integral": 0,
            "valores_invalidos_base_integral": {coluna: 0 for coluna in VALORES},
            "ausencias_recorte": {coluna: 0 for coluna in COLUNAS_ANALISE},
            "valores_negativos_recorte": {coluna: 0 for coluna in VALORES},
            "registros_por_funcao": {},
            "rotulos_reconstruidos_2025": {chave: 0 for chave in ["Funcao", "SubFuncao", "Programa", "Subtitulo"]},
            "rotulos_fallback_2025": {chave: 0 for chave in ["Funcao", "SubFuncao", "Programa", "Subtitulo"]},
        }
        return pd.DataFrame(columns=COLUNAS_ANALISE), auditoria_vazia

    partes: list[pd.DataFrame] = []

    registros_base_integral = 0
    registros_base_integral_por_ano = {ano: 0 for ano in ANOS_ANALISADOS}
    duplicados_id_base_integral = 0
    datas_invalidas_base_integral = 0
    valores_invalidos_base_integral = {coluna: 0 for coluna in VALORES}
    rotulos_reconstruidos_2025 = {chave: 0 for chave in ["Funcao", "SubFuncao", "Programa", "Subtitulo"]}
    rotulos_fallback_2025 = {chave: 0 for chave in ["Funcao", "SubFuncao", "Programa", "Subtitulo"]}

    ids_vistos: set[str] = set()

    mapas = {
        "funcao": {},
        "subfuncao": {},
        "subtitulo": {},
        "programa_contexto": {},
        "programa_global_sets": {},
        "programa_global": {},
    }

    for ano in ANOS_ANALISADOS:
        if ano == 2025:
            _finalizar_mapas(mapas)

        for arquivo in arquivos_por_ano[ano]:
            leitor = pd.read_csv(
                arquivo,
                sep=";",
                encoding="utf-8-sig",
                compression="zip",
                usecols=COLUNAS_ORIGEM,
                dtype=str,
                chunksize=75_000,
                low_memory=False,
            )

            for bruto in leitor:
                registros_base_integral += len(bruto)
                registros_base_integral_por_ano[ano] += len(bruto)

                # As relações de referência são construídas exclusivamente com
                # os rótulos realmente presentes na base oficial de 2024.
                if ano == 2024:
                    _atualizar_mapas_2024(bruto, mapas)

                # Auditoria de duplicidade na base integral.
                ids = bruto["Id"].astype("string").str.strip()
                ids_validos = ids[~ids.isna() & ids.ne("")]
                duplicados_id_base_integral += int(ids_validos.duplicated().sum())

                ids_unicos_chunk = ids_validos.drop_duplicates()
                duplicados_id_base_integral += sum(
                    1 for id_ in ids_unicos_chunk if str(id_) in ids_vistos
                )
                ids_vistos.update(str(id_) for id_ in ids_unicos_chunk)

                # Auditoria de datas inválidas: só conta quando havia conteúdo na origem.
                datas_origem = bruto["Data"].astype("string").str.strip()
                datas_convertidas = pd.to_datetime(datas_origem, dayfirst=True, errors="coerce")
                datas_invalidas_base_integral += int(
                    ((~datas_origem.isna()) & datas_origem.ne("") & datas_convertidas.isna()).sum()
                )

                # Auditoria monetária antes de qualquer agregação.
                for coluna in VALORES:
                    origem = bruto[coluna].astype("string").str.strip()
                    convertido = _moeda_para_float(origem)
                    valores_invalidos_base_integral[coluna] += int(
                        ((~origem.isna()) & origem.ne("") & convertido.isna()).sum()
                    )

                chunk, reconstruidos, fallbacks = _normalizar_chunk(bruto, ano, mapas)

                if ano == 2025:
                    for chave in rotulos_reconstruidos_2025:
                        rotulos_reconstruidos_2025[chave] += reconstruidos[chave]
                        rotulos_fallback_2025[chave] += fallbacks[chave]

                chunk = chunk[chunk["Funcao"].isin(AREAS_MONITORADAS)].copy()

                if not chunk.empty:
                    partes.append(chunk)

    if not partes:
        df = pd.DataFrame(columns=COLUNAS_ANALISE)
    else:
        df = pd.concat(partes, ignore_index=True)

        # Datas inválidas não podem participar das análises temporais.
        df = df.dropna(subset=["Data"])

        # O Id é único nos arquivos atuais; esta proteção evita contagem dupla
        # caso uma carga futura venha com repetição acidental.
        id_valido = df["Id"].notna() & df["Id"].astype("string").str.strip().ne("")
        duplicado_recorte = id_valido & df.duplicated(subset=["Id"], keep="first")
        df = df.loc[~duplicado_recorte].reset_index(drop=True)

    ausencias_recorte: dict[str, int] = {}
    for coluna in COLUNAS_ANALISE:
        if coluna in TEXTOS or coluna == "Id":
            ausencias_recorte[coluna] = int(_texto_vazio(df[coluna]).sum()) if not df.empty else 0
        else:
            ausencias_recorte[coluna] = int(df[coluna].isna().sum()) if not df.empty else 0

    valores_negativos_recorte = {
        coluna: int((df[coluna] < 0).sum()) if not df.empty else 0
        for coluna in VALORES
    }

    registros_por_funcao = (
        df["Funcao"].value_counts().sort_index().astype(int).to_dict()
        if not df.empty
        else {}
    )
    registros_recorte_por_ano = (
        df["Ano"].value_counts().sort_index().astype(int).to_dict()
        if not df.empty
        else {}
    )

    auditoria = {
        "registros_base_integral": int(registros_base_integral),
        "registros_recorte": int(len(df)),
        "registros_base_integral_por_ano": {int(k): int(v) for k, v in registros_base_integral_por_ano.items()},
        "registros_recorte_por_ano": {int(k): int(v) for k, v in registros_recorte_por_ano.items()},
        "duplicados_id_base_integral": int(duplicados_id_base_integral),
        "datas_invalidas_base_integral": int(datas_invalidas_base_integral),
        "valores_invalidos_base_integral": valores_invalidos_base_integral,
        "ausencias_recorte": ausencias_recorte,
        "valores_negativos_recorte": valores_negativos_recorte,
        "registros_por_funcao": registros_por_funcao,
        "rotulos_reconstruidos_2025": rotulos_reconstruidos_2025,
        "rotulos_fallback_2025": rotulos_fallback_2025,
    }

    return df, auditoria


@lru_cache(maxsize=1)
def carregar_base() -> pd.DataFrame:
    """Retorna o recorte temático 2024-2025 já preparado para o dashboard."""
    return _carregar_base_e_auditoria()[0]


@lru_cache(maxsize=1)
def auditoria_base() -> dict:
    """Retorna os indicadores de qualidade calculados durante a carga."""
    return _carregar_base_e_auditoria()[1]


def metadata() -> dict:
    df = carregar_base()
    auditoria = auditoria_base()

    if df.empty:
        return {
            "registros_base_integral": auditoria.get("registros_base_integral", 0),
            "registros_recorte": 0,
        }

    return {
        "registros_base_integral": auditoria["registros_base_integral"],
        "registros_recorte": int(len(df)),
        "data_minima": df["Data"].min().date().isoformat(),
        "data_maxima": df["Data"].max().date().isoformat(),
        "anos": sorted(int(ano) for ano in df["Ano"].dropna().unique()),
        "total_funcoes": int(df["Funcao"].nunique()),
        "total_localizadores": int(df["Subtitulo"].nunique(dropna=True)),
    }


def area_metadata(funcao: str) -> dict:
    df = carregar_base()
    area = df[df["Funcao"] == funcao]

    if area.empty:
        return {"data_minima": None, "data_maxima": None, "registros": 0, "anos": []}

    return {
        "data_minima": area["Data"].min().date().isoformat(),
        "data_maxima": area["Data"].max().date().isoformat(),
        "registros": int(len(area)),
        "anos": sorted(int(ano) for ano in area["Ano"].dropna().unique()),
    }


def _distinct(area: pd.DataFrame, coluna: str) -> list[str]:
    if area.empty:
        return []

    serie = area[coluna].dropna().astype(str).str.strip()
    return sorted(serie[serie.str.len() > 0].unique().tolist())


def opcoes_area(funcao: str) -> dict:
    df = carregar_base()
    area = df[df["Funcao"] == funcao]

    if area.empty:
        return {"anos": [], "regioes": [], "subfuncoes": [], "programas": [], "unidades": []}

    return {
        "anos": sorted(int(ano) for ano in area["Ano"].dropna().unique()),
        # O nome interno foi preservado para não quebrar callbacks existentes.
        # Na interface este campo é apresentado como "Localizador territorial".
        "regioes": _distinct(area, "Subtitulo"),
        "subfuncoes": _distinct(area, "SubFuncao"),
        "programas": _distinct(area, "Programa"),
        "unidades": _distinct(area, "UnidadeGestora"),
    }


def carregar_area(
    funcao: str,
    inicio: str | None = None,
    fim: str | None = None,
    anos: list[int] | list[str] | None = None,
    regioes: list[str] | None = None,
    subfuncoes: list[str] | None = None,
    programas: list[str] | None = None,
    unidades: list[str] | None = None,
) -> pd.DataFrame:
    df = carregar_base()
    if df.empty:
        return pd.DataFrame(columns=COLUNAS_ANALISE)

    area = df[df["Funcao"] == funcao]

    if anos:
        anos_int = {int(ano) for ano in anos}
        area = area[area["Ano"].isin(anos_int)]
    if inicio:
        area = area[area["Data"] >= pd.to_datetime(inicio)]
    if fim:
        area = area[area["Data"] <= pd.to_datetime(fim)]
    if regioes:
        area = area[area["Subtitulo"].isin(regioes)]
    if subfuncoes:
        area = area[area["SubFuncao"].isin(subfuncoes)]
    if programas:
        area = area[area["Programa"].isin(programas)]
    if unidades:
        area = area[area["UnidadeGestora"].isin(unidades)]

    return area.copy()


def registros_rastreaveis(df: pd.DataFrame) -> list[dict]:
    """
    Converte o recorte ativo em registros seguros para inspeção na POC.

    Não inclui CPF/CNPJ/NIS, favorecido, dados bancários ou outros campos
    pessoais. A tabela existe apenas para permitir rastrear os indicadores até
    os registros oficiais que os compõem.
    """
    if df.empty:
        return []

    tabela = df[COLUNAS_RASTREABILIDADE].copy()
    tabela["Ano"] = tabela["Ano"].astype("Int64")
    tabela["Data"] = tabela["Data"].dt.strftime("%d/%m/%Y")

    for coluna in VALORES:
        tabela[coluna] = tabela[coluna].round(2)

    tabela = tabela.where(pd.notna(tabela), None)
    return tabela.to_dict("records")


def resumo_funcoes(funcoes: list[str]) -> pd.DataFrame:
    df = carregar_base()
    if df.empty:
        return pd.DataFrame(
            columns=["Funcao", "ValorEmpenho", "ValorLiquidado", "ValorPago", "ValorRap", "Registros"]
        )

    return (
        df[df["Funcao"].isin(funcoes)]
        .groupby("Funcao", as_index=False)
        .agg(
            ValorEmpenho=("ValorEmpenho", "sum"),
            ValorLiquidado=("ValorLiquidado", "sum"),
            ValorPago=("ValorPago", "sum"),
            ValorRap=("ValorRap", "sum"),
            Registros=("Funcao", "size"),
        )
        .sort_values("ValorPago", ascending=False)
    )
