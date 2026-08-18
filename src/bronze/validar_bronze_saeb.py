from pathlib import Path
import hashlib

import pandas as pd


RAW_DIR = Path("data/raw/saeb")
BRONZE_DIR = Path("data/bronze/saeb")


CONFIG = {
    2007: {
        "arquivo_raw": "MEDIA_UF_2007.xlsx",
        "arquivo_bronze": "saeb_2007.parquet",
        "aba": "MEDIA_ESTADOS",
        "granularidade": "UF",
        "cabecalho_indice": 0,
        "linha_cabecalho_origem": 1,
        "linhas": 269,
        "colunas_fonte": 12,
        "sha256": "f90b8c89973c586d7adb88bcb01130017accb540bbc3edc5ce4739c5c1603667",
        "marcadores": [
            "ANO_SAEB",
            "CO_UF",
            "NO_UF",
            "DEPENDENCIA_ADM",
            "MEDIA_4_LP",
            "MEDIA_8_MT",
        ],
    },
    2009: {
        "arquivo_raw": "MEDIA_UF_2009.xlsx",
        "arquivo_bronze": "saeb_2009.parquet",
        "aba": "MEDIA_ESTADOS",
        "granularidade": "UF",
        "cabecalho_indice": 0,
        "linha_cabecalho_origem": 1,
        "linhas": 269,
        "colunas_fonte": 12,
        "sha256": "052bf375d052f200ffb932f668ffebb0faae68dca66156bb6d3063a08e8e5f6b",
        "marcadores": [
            "ANO_SAEB",
            "CO_UF",
            "NO_UF",
            "DEPENDENCIA_ADM",
            "MEDIA_4_LP",
            "MEDIA_8_MT",
        ],
    },
    2011: {
        "arquivo_raw": "TS_RESULTADO_UF_2011.csv",
        "arquivo_bronze": "saeb_2011.parquet",
        "aba": None,
        "granularidade": "UF",
        "cabecalho_indice": 0,
        "linha_cabecalho_origem": 1,
        "linhas": 4375,
        "colunas_fonte": 13,
        "sha256": "2e4b8e15279d645b4d19ea1acc5473fc73d968c69d54bbb9715e59f2d84fa8a7",
        "marcadores": [
            "ID_SAEB",
            "SIGLA_UF",
            "ID_UF",
            "ID_SERIE",
            "ID_TIPO_REDE",
            "MEDIA_LP",
            "MEDIA_MT",
        ],
    },
    2013: {
        "arquivo_raw": "TS_UF_2013.xlsx",
        "arquivo_bronze": "saeb_2013.parquet",
        "aba": "UF",
        "granularidade": "UF",
        "cabecalho_indice": 3,
        "linha_cabecalho_origem": 4,
        "linhas": 1706,
        "colunas_fonte": 10,
        "sha256": "42e3efe1a614dcb891c29681063b8f0d1a8336ef1477bde26663771b956fc8ca",
        "marcadores": [
            "UF",
            "REDE",
            "LOCALIZAÇÃO",
            "MÉDIAS DE PROFICIÊNCIA",
        ],
    },
    2015: {
        "arquivo_raw": "TS_UF_2015.xlsx",
        "arquivo_bronze": "saeb_2015.parquet",
        "aba": "UFs",
        "granularidade": "UF",
        "cabecalho_indice": 2,
        "linha_cabecalho_origem": 3,
        "linhas": 1706,
        "colunas_fonte": 10,
        "sha256": "33f947a87c6aacf8d3ac4e07ba9311f547f898f2585980c2aa0c91e2ae2a4521",
        "marcadores": [
            "UF",
            "REDE",
            "LOCALIZAÇÃO",
            "MÉDIAS DE PROFICIÊNCIA",
        ],
    },
    2017: {
        "arquivo_raw": "TS_UF_2017.xlsx",
        "arquivo_bronze": "saeb_2017.parquet",
        "aba": "TS_UF",
        "granularidade": "UF",
        "cabecalho_indice": 0,
        "linha_cabecalho_origem": 1,
        "linhas": 1702,
        "colunas_fonte": 70,
        "sha256": "143ec3a2cb6eda454412b4a7605d31d0b7d39b8631de3aa3b413932989127159",
        "marcadores": [
            "CO_UF",
            "NO_UF",
            "DEPENDENCIA_ADM",
            "LOCALIZACAO",
            "MEDIA_5_LP",
            "MEDIA_9_MT",
        ],
    },
    2019: {
        "arquivo_raw": "TS_UF_2019.xlsx",
        "arquivo_bronze": "saeb_2019.parquet",
        "aba": "Estados",
        "granularidade": "UF",
        "cabecalho_indice": 0,
        "linha_cabecalho_origem": 1,
        "linhas": 1551,
        "colunas_fonte": 156,
        "sha256": "a92e77b1ec6394a9c03a2007f10ccd687e81bffdc17ff226bb47523a5b390af6",
        "marcadores": [
            "CO_UF",
            "NO_UF",
            "DEPENDENCIA_ADM",
            "LOCALIZACAO",
            "MEDIA_2_LP",
            "MEDIA_5_LP",
            "MEDIA_9_MT",
        ],
    },
    2021: {
        "arquivo_raw": "TS_UF_2021.xlsx",
        "arquivo_bronze": "saeb_2021.parquet",
        "aba": "Estados",
        "granularidade": "UF",
        "cabecalho_indice": 0,
        "linha_cabecalho_origem": 1,
        "linhas": 1517,
        "colunas_fonte": 156,
        "sha256": "c724725e16746a5dfeb33cd7818ed69709c1ff687b6528cd8ee5ee67b025ee68",
        "marcadores": [
            "CO_UF",
            "NO_UF",
            "DEPENDENCIA_ADM",
            "LOCALIZACAO",
            "MEDIA_2_LP",
            "MEDIA_5_LP",
            "MEDIA_9_MT",
        ],
    },
    2023: {
        "arquivo_raw": "TS_ESCOLA_2023.csv",
        "arquivo_bronze": "saeb_2023.parquet",
        "aba": None,
        "granularidade": "ESCOLA",
        "cabecalho_indice": 0,
        "linha_cabecalho_origem": 1,
        "linhas": 70152,
        "colunas_fonte": 137,
        "sha256": "64dc8ca0b5b1a65b3ee40aacdfa473984f32f0e7794affcbbf488217b2fbfbf7",
        "marcadores": [
            "ID_SAEB",
            "ID_UF",
            "ID_MUNICIPIO",
            "ID_ESCOLA",
            "IN_PUBLICA",
            "MEDIA_5EF_LP",
            "MEDIA_9EF_MT",
        ],
    },
}


COLUNAS_TECNICAS = [
    "_fonte",
    "_sha256_arquivo",
    "_arquivo_origem",
    "_aba_origem",
    "_ano_referencia",
    "_granularidade_origem",
    "_indice_cabecalho_origem",
    "_linha_origem",
]


def calcular_sha256(caminho):
    sha256 = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(1024 * 1024):
            sha256.update(bloco)

    return sha256.hexdigest()


def colunas_fonte(df):
    return [
        coluna
        for coluna in df.columns
        if coluna.startswith("col_")
    ]


def validar_sequencia_colunas_fonte(df, quantidade_esperada):
    esperadas = [
        f"col_{indice:03d}"
        for indice in range(1, quantidade_esperada + 1)
    ]

    encontradas = colunas_fonte(df)

    if encontradas != esperadas:
        raise RuntimeError(
            "Sequência de colunas da fonte diferente da esperada.\n"
            f"Esperadas: {esperadas[:5]} ... {esperadas[-5:]}\n"
            f"Encontradas: {encontradas[:5]} ... {encontradas[-5:]}"
        )


def validar_marcadores_cabecalho(df, configuracao, ano):
    linha_origem = configuracao["linha_cabecalho_origem"]

    linha = df.loc[
        df["_linha_origem"] == linha_origem,
        colunas_fonte(df),
    ]

    if len(linha) != 1:
        raise RuntimeError(
            f"Não foi possível localizar uma única linha de cabeçalho "
            f"no SAEB {ano}. _linha_origem={linha_origem}"
        )

    valores = [
        str(valor)
        for valor in linha.iloc[0].tolist()
        if pd.notna(valor)
    ]

    texto = " | ".join(valores)

    faltantes = [
        marcador
        for marcador in configuracao["marcadores"]
        if marcador not in texto
    ]

    if faltantes:
        raise RuntimeError(
            f"Marcadores de cabeçalho ausentes no SAEB {ano}: {faltantes}"
        )


def validar_arquivo(ano, configuracao):
    raw = RAW_DIR / configuracao["arquivo_raw"]
    parquet = BRONZE_DIR / configuracao["arquivo_bronze"]

    if not raw.exists():
        raise RuntimeError(
            f"RAW ausente no SAEB {ano}: {raw}"
        )

    if not parquet.exists():
        raise RuntimeError(
            f"Parquet ausente no SAEB {ano}: {parquet}"
        )

    sha_atual = calcular_sha256(raw)

    if sha_atual != configuracao["sha256"]:
        raise RuntimeError(
            f"SHA-256 do RAW mudou no SAEB {ano}.\n"
            f"Esperado: {configuracao['sha256']}\n"
            f"Atual:    {sha_atual}"
        )

    df = pd.read_parquet(
        parquet,
        engine="pyarrow",
    )

    if df.empty:
        raise RuntimeError(
            f"Parquet vazio no SAEB {ano}."
        )

    if len(df) != configuracao["linhas"]:
        raise RuntimeError(
            f"Quantidade de linhas divergente no SAEB {ano}: "
            f"esperado={configuracao['linhas']}, encontrado={len(df)}"
        )

    faltantes = [
        coluna
        for coluna in COLUNAS_TECNICAS
        if coluna not in df.columns
    ]

    if faltantes:
        raise RuntimeError(
            f"Colunas técnicas ausentes no SAEB {ano}: {faltantes}"
        )

    if set(df["_fonte"].dropna().unique()) != {"SAEB"}:
        raise RuntimeError(
            f"_fonte inválida no SAEB {ano}."
        )

    if set(df["_sha256_arquivo"].dropna().unique()) != {
        configuracao["sha256"]
    }:
        raise RuntimeError(
            f"_sha256_arquivo inválido no SAEB {ano}."
        )

    if set(df["_arquivo_origem"].dropna().unique()) != {
        configuracao["arquivo_raw"]
    }:
        raise RuntimeError(
            f"_arquivo_origem inválido no SAEB {ano}."
        )

    abas = set(df["_aba_origem"].dropna().unique())

    if configuracao["aba"] is None:
        if abas:
            raise RuntimeError(
                f"_aba_origem deveria estar ausente no CSV do SAEB {ano}: "
                f"{abas}"
            )
    else:
        if abas != {configuracao["aba"]}:
            raise RuntimeError(
                f"_aba_origem inválido no SAEB {ano}: {abas}"
            )

    if set(df["_ano_referencia"].dropna().unique()) != {ano}:
        raise RuntimeError(
            f"_ano_referencia inválido no SAEB {ano}."
        )

    if set(
        df["_granularidade_origem"]
        .dropna()
        .unique()
    ) != {configuracao["granularidade"]}:
        raise RuntimeError(
            f"_granularidade_origem inválida no SAEB {ano}."
        )

    if set(
        df["_indice_cabecalho_origem"]
        .dropna()
        .unique()
    ) != {configuracao["cabecalho_indice"]}:
        raise RuntimeError(
            f"_indice_cabecalho_origem inválido no SAEB {ano}."
        )

    if df["_linha_origem"].isna().any():
        raise RuntimeError(
            f"_linha_origem possui valores ausentes no SAEB {ano}."
        )

    if df["_linha_origem"].duplicated().any():
        raise RuntimeError(
            f"_linha_origem possui duplicidades no SAEB {ano}."
        )

    if not df["_linha_origem"].is_monotonic_increasing:
        raise RuntimeError(
            f"_linha_origem não é monotônica no SAEB {ano}."
        )

    validar_sequencia_colunas_fonte(
        df,
        configuracao["colunas_fonte"],
    )

    validar_marcadores_cabecalho(
        df,
        configuracao,
        ano,
    )

    print(f"ANO {ano}")
    print("-" * 100)
    print(f"Linhas: {len(df):,}")
    print(f"Colunas da fonte: {configuracao['colunas_fonte']}")
    print(
        "Aba: "
        + (
            repr(configuracao["aba"])
            if configuracao["aba"] is not None
            else "não se aplica (CSV)"
        )
    )
    print(f"Granularidade: {configuracao['granularidade']}")
    print("SHA-256: OK")
    print("Status: OK")
    print()

    return len(df)


def main():
    print("=" * 110)
    print("VALIDAÇÃO FINAL — BRONZE SAEB")
    print("=" * 110)
    print()

    anos_esperados = list(CONFIG.keys())

    nomes_esperados = {
        configuracao["arquivo_bronze"]
        for configuracao in CONFIG.values()
    }

    nomes_encontrados = {
        arquivo.name
        for arquivo in BRONZE_DIR.glob("saeb_*.parquet")
    }

    if nomes_encontrados != nomes_esperados:
        raise RuntimeError(
            "Conjunto de Parquets do SAEB diferente do esperado.\n"
            f"Esperados: {sorted(nomes_esperados)}\n"
            f"Encontrados: {sorted(nomes_encontrados)}"
        )

    total_linhas = 0

    for ano in anos_esperados:
        total_linhas += validar_arquivo(
            ano,
            CONFIG[ano],
        )

    total_esperado = sum(
        configuracao["linhas"]
        for configuracao in CONFIG.values()
    )

    if total_linhas != total_esperado:
        raise RuntimeError(
            f"Total de linhas divergente: "
            f"esperado={total_esperado}, encontrado={total_linhas}"
        )

    print("=" * 110)
    print("RESUMO")
    print("=" * 110)
    print()
    print(f"Parquets encontrados: {len(nomes_encontrados)}")
    print(f"Parquets esperados: {len(nomes_esperados)}")
    print(f"Total de linhas Bronze: {total_linhas:,}")
    print()
    print("TODAS AS 9 EDIÇÕES FORAM VALIDADAS.")
    print("BRONZE DO SAEB: OK")
    print()


if __name__ == "__main__":
    main()
