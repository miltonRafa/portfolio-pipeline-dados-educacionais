from pathlib import Path
import hashlib

import pandas as pd


RAW_DIR = Path("data/raw/saeb")
BRONZE_DIR = Path("data/bronze/saeb")


CONFIG = {
    2007: {
        "arquivo": "MEDIA_UF_2007.xlsx",
        "tipo": "xlsx",
        "aba": "MEDIA_ESTADOS",
        "cabecalho_indice": 0,
        "granularidade": "UF",
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
        "arquivo": "MEDIA_UF_2009.xlsx",
        "tipo": "xlsx",
        "aba": "MEDIA_ESTADOS",
        "cabecalho_indice": 0,
        "granularidade": "UF",
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
        "arquivo": "TS_RESULTADO_UF_2011.csv",
        "tipo": "csv",
        "aba": None,
        "cabecalho_indice": 0,
        "granularidade": "UF",
        "encoding": "utf-8",
        "sep": ";",
        "colunas_esperadas": 13,
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
        "arquivo": "TS_UF_2013.xlsx",
        "tipo": "xlsx",
        "aba": "UF",
        "cabecalho_indice": 3,
        "granularidade": "UF",
        "marcadores": [
            "UF",
            "REDE",
            "LOCALIZAÇÃO",
            "MÉDIAS DE PROFICIÊNCIA",
            "LÍNGUA PORTUGUESA",
            "MATEMÁTICA",
        ],
    },
    2015: {
        "arquivo": "TS_UF_2015.xlsx",
        "tipo": "xlsx",
        "aba": "UFs",
        "cabecalho_indice": 2,
        "granularidade": "UF",
        "marcadores": [
            "UF",
            "REDE",
            "LOCALIZAÇÃO",
            "MÉDIAS DE PROFICIÊNCIA",
            "LÍNGUA PORTUGUESA",
            "MATEMÁTICA",
        ],
    },
    2017: {
        "arquivo": "TS_UF_2017.xlsx",
        "tipo": "xlsx",
        "aba": "TS_UF",
        "cabecalho_indice": 0,
        "granularidade": "UF",
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
        "arquivo": "TS_UF_2019.xlsx",
        "tipo": "xlsx",
        "aba": "Estados",
        "cabecalho_indice": 0,
        "granularidade": "UF",
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
        "arquivo": "TS_UF_2021.xlsx",
        "tipo": "xlsx",
        "aba": "Estados",
        "cabecalho_indice": 0,
        "granularidade": "UF",
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
        "arquivo": "TS_ESCOLA_2023.csv",
        "tipo": "csv",
        "aba": None,
        "cabecalho_indice": 0,
        "granularidade": "ESCOLA",
        "encoding": "cp1252",
        "sep": ";",
        "colunas_esperadas": 137,
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


def validar_arquivo(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo RAW não encontrado: {caminho}"
        )

    if not caminho.is_file():
        raise RuntimeError(
            f"O caminho RAW não representa um arquivo: {caminho}"
        )


def ler_xlsx(caminho, aba):
    excel = pd.ExcelFile(
        caminho,
        engine="openpyxl",
    )

    abas = excel.sheet_names

    if aba not in abas:
        raise RuntimeError(
            "\nAba auditada não encontrada.\n"
            f"Arquivo: {caminho.name}\n"
            f"Aba esperada: {aba!r}\n"
            f"Abas encontradas: {abas}"
        )

    return pd.read_excel(
        caminho,
        sheet_name=aba,
        header=None,
        engine="openpyxl",
        dtype=object,
    )


def ler_csv(caminho, encoding, sep):
    dados = pd.read_csv(
        caminho,
        sep=sep,
        encoding=encoding,
        header=None,
        dtype="string",
        keep_default_na=False,
        na_filter=False,
        skip_blank_lines=False,
        low_memory=False,
    )

    # Campos realmente vazios passam a valores ausentes.
    # Nenhuma limpeza de espaços ou conteúdo textual é aplicada.
    return dados.replace("", pd.NA)


def validar_quantidade_colunas_csv(
    dados,
    ano,
    quantidade_esperada,
):
    quantidade_encontrada = len(dados.columns)

    if quantidade_encontrada != quantidade_esperada:
        raise RuntimeError(
            "\nQuantidade de colunas do CSV diferente da auditada.\n"
            f"Ano: {ano}\n"
            f"Esperado: {quantidade_esperada}\n"
            f"Encontrado: {quantidade_encontrada}"
        )


def texto_primeiras_linhas(dados, limite=10):
    amostra = dados.head(limite)

    valores = []

    for valor in amostra.to_numpy().ravel():
        if pd.isna(valor):
            continue

        valores.append(str(valor))

    return " | ".join(valores)


def validar_marcadores(
    dados,
    ano,
    marcadores,
):
    texto = texto_primeiras_linhas(
        dados,
        limite=10,
    )

    faltantes = [
        marcador
        for marcador in marcadores
        if marcador not in texto
    ]

    if faltantes:
        raise RuntimeError(
            "\nEstrutura diferente da auditada.\n"
            f"Ano: {ano}\n"
            "Marcadores não encontrados nas primeiras linhas: "
            f"{faltantes}"
        )


def validar_ano_quando_disponivel(
    dados,
    ano,
):
    texto = texto_primeiras_linhas(
        dados,
        limite=20,
    )

    # 2013 e 2015 registram o ano no título da planilha.
    if ano in {2013, 2015}:
        if str(ano) not in texto:
            raise RuntimeError(
                f"Ano {ano} não encontrado no título/estrutura inicial."
            )

        return

    # Nos demais arquivos o ano pode aparecer como valor de uma
    # coluna própria ou ser identificado pela edição/arquivo.
    if ano in {2007, 2009, 2011, 2023}:
        if str(ano) not in texto:
            raise RuntimeError(
                f"Ano {ano} não encontrado nas primeiras linhas da fonte."
            )


def preparar_bronze(
    dados,
    ano,
    configuracao,
    sha256_arquivo,
):
    quantidade_colunas_fonte = len(
        dados.columns
    )

    # A posição física original é registrada antes de qualquer
    # remoção de linhas completamente vazias.
    dados = dados.copy()

    dados["_linha_origem"] = (
        dados.index + 1
    )

    colunas_fonte = [
        f"col_{indice:03d}"
        for indice in range(
            1,
            quantidade_colunas_fonte + 1,
        )
    ]

    dados.columns = [
        *colunas_fonte,
        "_linha_origem",
    ]

    # Remove somente linhas cuja parte substantiva da fonte
    # está completamente vazia.
    mascara_vazia = (
        dados[colunas_fonte]
        .isna()
        .all(axis=1)
    )

    dados = (
        dados.loc[~mascara_vazia]
        .copy()
    )

    # Preservação técnica das células como texto.
    for coluna in colunas_fonte:
        dados[coluna] = (
            dados[coluna]
            .astype("string")
        )

    dados.insert(
        0,
        "_fonte",
        "SAEB",
    )

    dados.insert(
        1,
        "_sha256_arquivo",
        sha256_arquivo,
    )

    dados.insert(
        2,
        "_arquivo_origem",
        configuracao["arquivo"],
    )

    dados.insert(
        3,
        "_aba_origem",
        (
            configuracao["aba"]
            if configuracao["aba"] is not None
            else pd.NA
        ),
    )

    dados.insert(
        4,
        "_ano_referencia",
        ano,
    )

    dados.insert(
        5,
        "_granularidade_origem",
        configuracao["granularidade"],
    )

    dados.insert(
        6,
        "_indice_cabecalho_origem",
        configuracao["cabecalho_indice"],
    )

    return dados


def validar_bronze_em_memoria(
    dados,
    ano,
    configuracao,
    sha256_arquivo,
):
    if dados.empty:
        raise RuntimeError(
            f"Bronze do SAEB {ano} ficou vazia."
        )

    faltantes = [
        coluna
        for coluna in COLUNAS_TECNICAS
        if coluna not in dados.columns
    ]

    if faltantes:
        raise RuntimeError(
            f"Colunas técnicas ausentes em {ano}: {faltantes}"
        )

    if set(dados["_fonte"].dropna().unique()) != {"SAEB"}:
        raise RuntimeError(
            f"_fonte inválida no SAEB {ano}."
        )

    if set(
        dados["_arquivo_origem"]
        .dropna()
        .unique()
    ) != {configuracao["arquivo"]}:
        raise RuntimeError(
            f"_arquivo_origem inválido no SAEB {ano}."
        )

    if set(
        dados["_ano_referencia"]
        .dropna()
        .unique()
    ) != {ano}:
        raise RuntimeError(
            f"_ano_referencia inválido no SAEB {ano}."
        )

    if set(
        dados["_granularidade_origem"]
        .dropna()
        .unique()
    ) != {configuracao["granularidade"]}:
        raise RuntimeError(
            f"_granularidade_origem inválida no SAEB {ano}."
        )

    if set(
        dados["_sha256_arquivo"]
        .dropna()
        .unique()
    ) != {sha256_arquivo}:
        raise RuntimeError(
            f"SHA-256 inconsistente no SAEB {ano}."
        )

    if dados["_linha_origem"].isna().any():
        raise RuntimeError(
            f"_linha_origem possui ausências no SAEB {ano}."
        )

    if dados["_linha_origem"].duplicated().any():
        raise RuntimeError(
            f"_linha_origem possui duplicidades no SAEB {ano}."
        )

    if not dados["_linha_origem"].is_monotonic_increasing:
        raise RuntimeError(
            f"_linha_origem fora de ordem no SAEB {ano}."
        )


def validar_parquet(
    caminho,
    ano,
    linhas_esperadas,
    colunas_fonte_esperadas,
    sha256_arquivo,
):
    if not caminho.exists():
        raise RuntimeError(
            f"Parquet não foi criado: {caminho}"
        )

    dados = pd.read_parquet(
        caminho,
        engine="pyarrow",
    )

    if len(dados) != linhas_esperadas:
        raise RuntimeError(
            f"Linhas divergentes após releitura do SAEB {ano}: "
            f"esperado={linhas_esperadas}, encontrado={len(dados)}"
        )

    colunas_fonte = [
        coluna
        for coluna in dados.columns
        if coluna.startswith("col_")
    ]

    if len(colunas_fonte) != colunas_fonte_esperadas:
        raise RuntimeError(
            f"Colunas da fonte divergentes após releitura do SAEB {ano}: "
            f"esperado={colunas_fonte_esperadas}, "
            f"encontrado={len(colunas_fonte)}"
        )

    hashes = set(
        dados["_sha256_arquivo"]
        .dropna()
        .unique()
    )

    if hashes != {sha256_arquivo}:
        raise RuntimeError(
            f"SHA-256 divergente após releitura do SAEB {ano}."
        )


def processar_ano(
    ano,
    configuracao,
):
    caminho_raw = (
        RAW_DIR
        / configuracao["arquivo"]
    )

    validar_arquivo(
        caminho_raw
    )

    sha256_arquivo = calcular_sha256(
        caminho_raw
    )

    if configuracao["tipo"] == "xlsx":
        dados = ler_xlsx(
            caminho_raw,
            configuracao["aba"],
        )

    elif configuracao["tipo"] == "csv":
        dados = ler_csv(
            caminho_raw,
            configuracao["encoding"],
            configuracao["sep"],
        )

        validar_quantidade_colunas_csv(
            dados=dados,
            ano=ano,
            quantidade_esperada=(
                configuracao[
                    "colunas_esperadas"
                ]
            ),
        )

    else:
        raise RuntimeError(
            f"Tipo de fonte não suportado em {ano}: "
            f"{configuracao['tipo']}"
        )

    if dados.empty:
        raise RuntimeError(
            f"Fonte SAEB {ano} está vazia."
        )

    validar_marcadores(
        dados=dados,
        ano=ano,
        marcadores=configuracao["marcadores"],
    )

    validar_ano_quando_disponivel(
        dados=dados,
        ano=ano,
    )

    quantidade_colunas_fonte = len(
        dados.columns
    )

    bronze = preparar_bronze(
        dados=dados,
        ano=ano,
        configuracao=configuracao,
        sha256_arquivo=sha256_arquivo,
    )

    validar_bronze_em_memoria(
        dados=bronze,
        ano=ano,
        configuracao=configuracao,
        sha256_arquivo=sha256_arquivo,
    )

    destino = (
        BRONZE_DIR
        / f"saeb_{ano}.parquet"
    )

    bronze.to_parquet(
        destino,
        engine="pyarrow",
        compression="snappy",
        index=False,
    )

    validar_parquet(
        caminho=destino,
        ano=ano,
        linhas_esperadas=len(bronze),
        colunas_fonte_esperadas=quantidade_colunas_fonte,
        sha256_arquivo=sha256_arquivo,
    )

    print(
        f"[OK] SAEB {ano}"
    )
    print(
        f"     Arquivo: {configuracao['arquivo']}"
    )
    print(
        "     Aba: "
        + (
            repr(configuracao["aba"])
            if configuracao["aba"] is not None
            else "não se aplica (CSV)"
        )
    )
    print(
        f"     Granularidade: {configuracao['granularidade']}"
    )

    if configuracao["tipo"] == "csv":
        print(
            f"     Codificação: {configuracao['encoding']}"
        )
        print(
            f"     Delimitador: {configuracao['sep']!r}"
        )

    print(
        f"     Linhas Bronze: {len(bronze):,}"
    )
    print(
        f"     Colunas fonte: {quantidade_colunas_fonte}"
    )
    print(
        f"     SHA-256: {sha256_arquivo}"
    )
    print(
        f"     Destino: {destino}"
    )
    print()


def main():
    print("=" * 110)
    print(
        "CAMADA BRONZE — INGESTÃO DO SAEB"
    )
    print("=" * 110)
    print()

    BRONZE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    anos_esperados = [
        2007,
        2009,
        2011,
        2013,
        2015,
        2017,
        2019,
        2021,
        2023,
    ]

    if list(CONFIG.keys()) != anos_esperados:
        raise RuntimeError(
            "CONFIG do SAEB está diferente da série esperada."
        )

    for ano, configuracao in CONFIG.items():
        processar_ano(
            ano=ano,
            configuracao=configuracao,
        )

    parquets = sorted(
        BRONZE_DIR.glob(
            "saeb_*.parquet"
        )
    )

    nomes_esperados = {
        f"saeb_{ano}.parquet"
        for ano in anos_esperados
    }

    nomes_encontrados = {
        arquivo.name
        for arquivo in parquets
    }

    if nomes_encontrados != nomes_esperados:
        raise RuntimeError(
            "\nConjunto de Parquets do SAEB diferente do esperado.\n"
            f"Esperados: {sorted(nomes_esperados)}\n"
            f"Encontrados: {sorted(nomes_encontrados)}"
        )

    print("=" * 110)
    print(
        f"ARQUIVOS PROCESSADOS: {len(parquets)}"
    )
    print(
        f"ARQUIVOS ESPERADOS: {len(anos_esperados)}"
    )
    print(
        "INGESTÃO DO SAEB CONCLUÍDA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
