from pathlib import Path

import pandas as pd


BRONZE_DIR = Path("data/bronze/saeb")
SILVER_DIR = Path("data/silver/saeb")
OUTPUT_FILE = SILVER_DIR / "saeb_2007_2023.parquet"

ANOS = [2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023]

ARQUIVOS = {
    2007: BRONZE_DIR / "saeb_2007.parquet",
    2009: BRONZE_DIR / "saeb_2009.parquet",
    2011: BRONZE_DIR / "saeb_2011.parquet",
    2013: BRONZE_DIR / "saeb_2013.parquet",
    2015: BRONZE_DIR / "saeb_2015.parquet",
    2017: BRONZE_DIR / "saeb_2017.parquet",
    2019: BRONZE_DIR / "saeb_2019.parquet",
    2021: BRONZE_DIR / "saeb_2021.parquet",
    2023: BRONZE_DIR / "saeb_2023_resultados_uf.parquet",
}

UF_CODIGO_SIGLA = {
    11: "RO",
    12: "AC",
    13: "AM",
    14: "RR",
    15: "PA",
    16: "AP",
    17: "TO",
    21: "MA",
    22: "PI",
    23: "CE",
    24: "RN",
    25: "PB",
    26: "PE",
    27: "AL",
    28: "SE",
    29: "BA",
    31: "MG",
    32: "ES",
    33: "RJ",
    35: "SP",
    41: "PR",
    42: "SC",
    43: "RS",
    50: "MS",
    51: "MT",
    52: "GO",
    53: "DF",
}

UF_NOME_SIGLA = {
    "ACRE": "AC",
    "ALAGOAS": "AL",
    "AMAPA": "AP",
    "AMAZONAS": "AM",
    "BAHIA": "BA",
    "CEARA": "CE",
    "DISTRITO FEDERAL": "DF",
    "ESPIRITO SANTO": "ES",
    "GOIAS": "GO",
    "MARANHAO": "MA",
    "MATO GROSSO": "MT",
    "MATO GROSSO DO SUL": "MS",
    "MINAS GERAIS": "MG",
    "PARA": "PA",
    "PARAIBA": "PB",
    "PARANA": "PR",
    "PERNAMBUCO": "PE",
    "PIAUI": "PI",
    "RIO DE JANEIRO": "RJ",
    "RIO GRANDE DO NORTE": "RN",
    "RIO GRANDE DO SUL": "RS",
    "RONDONIA": "RO",
    "RORAIMA": "RR",
    "SANTA CATARINA": "SC",
    "SAO PAULO": "SP",
    "SERGIPE": "SE",
    "TOCANTINS": "TO",
}

UFS = set(UF_CODIGO_SIGLA.values())

ETAPAS = {
    "ANOS_INICIAIS": {
        "DISCIPLINAS": {
            "LP": None,
            "MT": None,
        }
    },
    "ANOS_FINAIS": {
        "DISCIPLINAS": {
            "LP": None,
            "MT": None,
        }
    },
}


def remover_acentos(texto):
    import unicodedata

    normalizado = unicodedata.normalize(
        "NFKD",
        str(texto),
    )

    return "".join(
        caractere
        for caractere in normalizado
        if not unicodedata.combining(
            caractere
        )
    )


def texto(valor):
    if pd.isna(valor):
        return None

    return str(valor).strip()


def numero(valor):
    valor_texto = texto(valor)

    if valor_texto is None:
        return None

    if valor_texto in {"", "-", "--"}:
        return None

    valor_texto = valor_texto.replace(
        ",",
        ".",
    )

    try:
        return float(
            valor_texto
        )
    except ValueError:
        return None


def inteiro(valor):
    n = numero(valor)

    if n is None:
        return None

    return int(n)


def identificar_colunas_origem(df):
    return [
        coluna
        for coluna in df.columns
        if str(coluna).startswith("col_")
    ]


def obter_indice_cabecalho(df):
    valores = (
        df["_indice_cabecalho_origem"]
        .dropna()
        .unique()
        .tolist()
    )

    if len(valores) != 1:
        raise RuntimeError(
            "Não foi possível determinar um único "
            "_indice_cabecalho_origem."
        )

    return int(
        valores[0]
    )


def construir_mapa_cabecalho(df):
    indice = obter_indice_cabecalho(
        df
    )

    colunas_origem = identificar_colunas_origem(
        df
    )

    if indice < 0 or indice >= len(df):
        raise RuntimeError(
            f"Índice de cabeçalho inválido: {indice}"
        )

    linha = df.iloc[
        indice
    ]

    mapa = {}

    for coluna in colunas_origem:
        valor = texto(
            linha[coluna]
        )

        if valor:
            mapa[
                valor
            ] = coluna

    return mapa


def linhas_dados(df):
    indice = obter_indice_cabecalho(
        df
    )

    linha_fisica_cabecalho = (
        indice + 1
    )

    return df[
        df["_linha_origem"]
        > linha_fisica_cabecalho
    ].copy()


def obter_coluna(mapa, nome):
    if nome not in mapa:
        raise RuntimeError(
            f"Variável {nome!r} não encontrada no cabeçalho."
        )

    return mapa[
        nome
    ]


def obter_uf(linha, mapa):
    if "CO_UF" in mapa:
        codigo = inteiro(
            linha[
                mapa["CO_UF"]
            ]
        )

        if codigo in UF_CODIGO_SIGLA:
            return UF_CODIGO_SIGLA[
                codigo
            ]

    if "ID_UF" in mapa:
        codigo = inteiro(
            linha[
                mapa["ID_UF"]
            ]
        )

        if codigo in UF_CODIGO_SIGLA:
            return UF_CODIGO_SIGLA[
                codigo
            ]

    if "SIGLA_UF" in mapa:
        sigla = texto(
            linha[
                mapa["SIGLA_UF"]
            ]
        )

        if sigla:
            sigla = sigla.upper()

            if sigla in UFS:
                return sigla

    if "NO_UF" in mapa:
        nome = texto(
            linha[
                mapa["NO_UF"]
            ]
        )

        if nome:
            chave = remover_acentos(
                nome
            ).upper()

            return UF_NOME_SIGLA.get(
                chave
            )

    return None


def obter_uf_por_nome(valor):
    nome = texto(
        valor
    )

    if not nome:
        return None

    chave = remover_acentos(
        nome
    ).upper()

    return UF_NOME_SIGLA.get(
        chave
    )


def valor_origem(linha, mapa, variavel):
    coluna = obter_coluna(
        mapa,
        variavel,
    )

    return linha[
        coluna
    ], coluna


def origem_comum(linha):
    def obter(nome):
        if nome not in linha.index:
            return None

        return linha[nome]

    return {
        "ARQUIVO_ORIGEM": obter(
            "_arquivo_origem"
        ),
        "ABA_ORIGEM": obter(
            "_aba_origem"
        ),
        "LINHA_ORIGEM_BRONZE": inteiro(
            obter("_linha_origem")
        ),
        "GRANULARIDADE_ORIGEM": obter(
            "_granularidade_origem"
        ),
    }


def criar_registro(
    *,
    ano,
    uf,
    etapa,
    disciplina,
    valor,
    coluna_origem,
    rede_origem,
    localizacao_origem,
    capital_origem,
    linha,
):
    origem = origem_comum(
        linha
    )

    return {
        "ANO": int(ano),
        "UF": uf,
        "ETAPA": etapa,
        "REDE": "PUBLICA",
        "DISCIPLINA": disciplina,
        "PROFICIENCIA": valor,
        "REDE_ORIGEM": rede_origem,
        "LOCALIZACAO_ORIGEM": localizacao_origem,
        "CAPITAL_ORIGEM": capital_origem,
        "ARQUIVO_ORIGEM": origem["ARQUIVO_ORIGEM"],
        "ABA_ORIGEM": origem["ABA_ORIGEM"],
        "LINHA_ORIGEM_BRONZE": origem["LINHA_ORIGEM_BRONZE"],
        "COLUNA_ORIGEM": coluna_origem,
        "GRANULARIDADE_ORIGEM": origem["GRANULARIDADE_ORIGEM"],
    }


def transformar_2007_2009(ano, df):
    mapa = construir_mapa_cabecalho(
        df
    )

    dados = linhas_dados(
        df
    )

    rede_col = obter_coluna(
        mapa,
        "DEPENDENCIA_ADM",
    )
    loc_col = obter_coluna(
        mapa,
        "LOCALIZACAO",
    )
    cap_col = obter_coluna(
        mapa,
        "CAPITAL",
    )

    alvo = dados[
        (
            dados[rede_col]
            .astype(str)
            .str.strip()
            == "Total - Estadual e Municipal"
        )
        & (
            dados[loc_col]
            .astype(str)
            .str.strip()
            == "Total"
        )
        & (
            dados[cap_col]
            .astype(str)
            .str.strip()
            == "Total"
        )
    ].copy()

    metricas = {
        ("ANOS_INICIAIS", "LP"): "MEDIA_4_LP",
        ("ANOS_INICIAIS", "MT"): "MEDIA_4_MT",
        ("ANOS_FINAIS", "LP"): "MEDIA_8_LP",
        ("ANOS_FINAIS", "MT"): "MEDIA_8_MT",
    }

    registros = []

    for _, linha in alvo.iterrows():
        uf = obter_uf(
            linha,
            mapa,
        )

        if uf not in UFS:
            continue

        for (
            etapa,
            disciplina,
        ), variavel in metricas.items():
            bruto, coluna = valor_origem(
                linha,
                mapa,
                variavel,
            )

            valor = numero(
                bruto
            )

            registros.append(
                criar_registro(
                    ano=ano,
                    uf=uf,
                    etapa=etapa,
                    disciplina=disciplina,
                    valor=valor,
                    coluna_origem=coluna,
                    rede_origem=texto(
                        linha[rede_col]
                    ),
                    localizacao_origem=texto(
                        linha[loc_col]
                    ),
                    capital_origem=texto(
                        linha[cap_col]
                    ),
                    linha=linha,
                )
            )

    return registros


def transformar_2011(df):
    mapa = construir_mapa_cabecalho(
        df
    )

    dados = linhas_dados(
        df
    )

    serie_col = obter_coluna(
        mapa,
        "ID_SERIE",
    )
    rede_col = obter_coluna(
        mapa,
        "ID_TIPO_REDE",
    )
    loc_col = obter_coluna(
        mapa,
        "ID_LOCALIZACAO",
    )
    cap_col = obter_coluna(
        mapa,
        "ID_CAPITAL",
    )

    configuracoes = {
        "ANOS_INICIAIS": 5,
        "ANOS_FINAIS": 9,
    }

    registros = []

    for etapa, serie in configuracoes.items():
        alvo = dados[
            (
                dados[serie_col]
                .map(inteiro)
                == serie
            )
            & (
                dados[rede_col]
                .map(inteiro)
                == 5
            )
            & (
                dados[loc_col]
                .map(inteiro)
                == 0
            )
            & (
                dados[cap_col]
                .map(inteiro)
                == 0
            )
        ].copy()

        for _, linha in alvo.iterrows():
            uf = obter_uf(
                linha,
                mapa,
            )

            if uf not in UFS:
                continue

            for disciplina, variavel in {
                "LP": "MEDIA_LP",
                "MT": "MEDIA_MT",
            }.items():
                bruto, coluna = valor_origem(
                    linha,
                    mapa,
                    variavel,
                )

                registros.append(
                    criar_registro(
                        ano=2011,
                        uf=uf,
                        etapa=etapa,
                        disciplina=disciplina,
                        valor=numero(bruto),
                        coluna_origem=coluna,
                        rede_origem=texto(
                            linha[rede_col]
                        ),
                        localizacao_origem=texto(
                            linha[loc_col]
                        ),
                        capital_origem=texto(
                            linha[cap_col]
                        ),
                        linha=linha,
                    )
                )

    return registros


def transformar_2013_2015(ano, df):
    """
    2013 e 2015 usam cabeçalho hierárquico em três linhas.

    A linha registrada em _indice_cabecalho_origem identifica o início
    do cabeçalho, mas não contém nomes técnicos como DEPENDENCIA_ADM ou
    MEDIA_5_LP. A auditoria da Bronze confirmou a estrutura física:

    col_001 = UF
    col_002 = REDE
    col_003 = LOCALIZAÇÃO
    col_004 = CAPITAL
    col_005 = Anos Iniciais / Língua Portuguesa
    col_006 = Anos Iniciais / Matemática
    col_007 = Anos Finais / Língua Portuguesa
    col_008 = Anos Finais / Matemática

    Por isso, a Silver usa essas posições explicitamente, em vez de
    inventar cabeçalhos técnicos que não existem na fonte.
    """
    colunas_necessarias = {
        "col_001",
        "col_002",
        "col_003",
        "col_004",
        "col_005",
        "col_006",
        "col_007",
        "col_008",
    }

    faltantes = sorted(
        colunas_necessarias.difference(
            df.columns
        )
    )

    if faltantes:
        raise RuntimeError(
            f"SAEB {ano}: colunas auditadas ausentes: {faltantes}"
        )

    # 2013: início do cabeçalho na linha física 4 e dados após as
    # três linhas hierárquicas (4, 5 e 6).
    # 2015: início na linha física 3 e dados após as linhas 3, 4 e 5.
    indice = obter_indice_cabecalho(
        df
    )

    primeira_linha_dados = (
        indice + 4
    )

    dados = df[
        df["_linha_origem"]
        >= primeira_linha_dados
    ].copy()

    alvo = dados[
        (
            dados["col_002"]
            .astype(str)
            .str.strip()
            == "Total - Federal, Estadual e Municipal"
        )
        & (
            dados["col_003"]
            .astype(str)
            .str.strip()
            == "Total"
        )
        & (
            dados["col_004"]
            .astype(str)
            .str.strip()
            == "Total"
        )
    ].copy()

    metricas = {
        ("ANOS_INICIAIS", "LP"): "col_005",
        ("ANOS_INICIAIS", "MT"): "col_006",
        ("ANOS_FINAIS", "LP"): "col_007",
        ("ANOS_FINAIS", "MT"): "col_008",
    }

    registros = []

    for _, linha in alvo.iterrows():
        uf = obter_uf_por_nome(
            linha["col_001"]
        )

        if uf not in UFS:
            continue

        for (
            etapa,
            disciplina,
        ), coluna_origem in metricas.items():
            valor = numero(
                linha[
                    coluna_origem
                ]
            )

            # Nota específica da fonte de 2015:
            # zero significa que não foi possível calcular a média
            # para aquele estrato. Essa regra não é aplicada aos
            # demais anos.
            if ano == 2015 and valor == 0:
                valor = None

            registros.append(
                criar_registro(
                    ano=ano,
                    uf=uf,
                    etapa=etapa,
                    disciplina=disciplina,
                    valor=valor,
                    coluna_origem=coluna_origem,
                    rede_origem=texto(
                        linha["col_002"]
                    ),
                    localizacao_origem=texto(
                        linha["col_003"]
                    ),
                    capital_origem=texto(
                        linha["col_004"]
                    ),
                    linha=linha,
                )
            )

    return registros


def transformar_2013_2023(ano, df):
    mapa = construir_mapa_cabecalho(
        df
    )

    dados = linhas_dados(
        df
    )

    rede_col = obter_coluna(
        mapa,
        "DEPENDENCIA_ADM",
    )
    loc_col = obter_coluna(
        mapa,
        "LOCALIZACAO",
    )
    cap_col = obter_coluna(
        mapa,
        "CAPITAL",
    )

    alvo = dados[
        (
            dados[rede_col]
            .astype(str)
            .str.strip()
            == "Total - Federal, Estadual e Municipal"
        )
        & (
            dados[loc_col]
            .astype(str)
            .str.strip()
            == "Total"
        )
        & (
            dados[cap_col]
            .astype(str)
            .str.strip()
            == "Total"
        )
    ].copy()

    metricas = {
        ("ANOS_INICIAIS", "LP"): "MEDIA_5_LP",
        ("ANOS_INICIAIS", "MT"): "MEDIA_5_MT",
        ("ANOS_FINAIS", "LP"): "MEDIA_9_LP",
        ("ANOS_FINAIS", "MT"): "MEDIA_9_MT",
    }

    registros = []

    for _, linha in alvo.iterrows():
        uf = obter_uf(
            linha,
            mapa,
        )

        if uf not in UFS:
            continue

        for (
            etapa,
            disciplina,
        ), variavel in metricas.items():
            bruto, coluna = valor_origem(
                linha,
                mapa,
                variavel,
            )

            valor = numero(
                bruto
            )

            # Regra específica da fonte Saeb 2015:
            # valor 0 significa que a média não pôde ser calculada
            # para o estrato. Não é uma regra aplicada aos demais anos.
            if ano == 2015 and valor == 0:
                valor = None

            registros.append(
                criar_registro(
                    ano=ano,
                    uf=uf,
                    etapa=etapa,
                    disciplina=disciplina,
                    valor=valor,
                    coluna_origem=coluna,
                    rede_origem=texto(
                        linha[rede_col]
                    ),
                    localizacao_origem=texto(
                        linha[loc_col]
                    ),
                    capital_origem=texto(
                        linha[cap_col]
                    ),
                    linha=linha,
                )
            )

    return registros


def validar_pre_gravacao(silver):
    esperado_linhas = (
        len(ANOS)
        * 27
        * 2
        * 2
    )

    if len(silver) != esperado_linhas:
        raise RuntimeError(
            f"Quantidade de linhas inesperada: "
            f"{len(silver)}; esperado={esperado_linhas}."
        )

    if set(silver["ANO"]) != set(ANOS):
        raise RuntimeError(
            "Conjunto de anos da Silver é diferente do esperado."
        )

    if set(silver["UF"]) != UFS:
        raise RuntimeError(
            "Conjunto global de UFs da Silver é diferente das 27 UFs."
        )

    if set(silver["ETAPA"]) != {
        "ANOS_INICIAIS",
        "ANOS_FINAIS",
    }:
        raise RuntimeError(
            "Etapas da Silver são diferentes do esperado."
        )

    if set(silver["DISCIPLINA"]) != {
        "LP",
        "MT",
    }:
        raise RuntimeError(
            "Disciplinas da Silver são diferentes do esperado."
        )

    if set(silver["REDE"]) != {
        "PUBLICA",
    }:
        raise RuntimeError(
            "Rede canônica diferente de PUBLICA."
        )

    chave = [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "DISCIPLINA",
    ]

    duplicadas = int(
        silver.duplicated(
            subset=chave,
            keep=False,
        ).sum()
    )

    if duplicadas:
        raise RuntimeError(
            f"Há {duplicadas} linhas duplicadas no grão analítico."
        )

    por_ano = (
        silver.groupby(
            "ANO"
        )
        .size()
        .to_dict()
    )

    erros = {
        ano: quantidade
        for ano, quantidade in por_ano.items()
        if quantidade != 108
    }

    if erros:
        raise RuntimeError(
            f"Quantidade por ano diferente de 108: {erros}"
        )

    por_ano_etapa = (
        silver.groupby(
            [
                "ANO",
                "ETAPA",
            ]
        )["UF"]
        .nunique()
    )

    if not (
        por_ano_etapa
        == 27
    ).all():
        raise RuntimeError(
            "Nem todos os pares ano/etapa possuem 27 UFs."
        )

    ausentes = int(
        silver["PROFICIENCIA"]
        .isna()
        .sum()
    )

    if ausentes:
        raise RuntimeError(
            f"Há {ausentes} proficiências ausentes na Silver."
        )

    fora_dominio = silver[
        ~silver["PROFICIENCIA"]
        .between(
            0,
            500,
            inclusive="both",
        )
    ]

    if not fora_dominio.empty:
        raise RuntimeError(
            "Há proficiências fora do domínio plausível 0–500."
        )


def main():
    print("=" * 110)
    print(
        "TRANSFORMAÇÃO SILVER — SAEB 2007–2023"
    )
    print("=" * 110)
    print()

    registros = []

    for ano in ANOS:
        arquivo = ARQUIVOS[
            ano
        ]

        if not arquivo.exists():
            raise FileNotFoundError(
                f"Bronze do ano {ano} não encontrada: {arquivo}"
            )

        print(
            f"Lendo {ano}: {arquivo}"
        )

        df = pd.read_parquet(
            arquivo
        )

        if ano in {
            2007,
            2009,
        }:
            registros.extend(
                transformar_2007_2009(
                    ano,
                    df,
                )
            )

        elif ano == 2011:
            registros.extend(
                transformar_2011(
                    df
                )
            )

        elif ano in {
            2013,
            2015,
        }:
            registros.extend(
                transformar_2013_2015(
                    ano,
                    df,
                )
            )

        else:
            registros.extend(
                transformar_2013_2023(
                    ano,
                    df,
                )
            )

    silver = pd.DataFrame(
        registros
    )

    silver["PROFICIENCIA"] = (
        pd.to_numeric(
            silver["PROFICIENCIA"],
            errors="coerce",
        )
        .round(2)
    )

    silver = silver.sort_values(
        [
            "ANO",
            "UF",
            "ETAPA",
            "DISCIPLINA",
        ]
    ).reset_index(
        drop=True
    )

    validar_pre_gravacao(
        silver
    )

    SILVER_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    silver.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow",
        compression="snappy",
    )

    releitura = pd.read_parquet(
        OUTPUT_FILE
    )

    if len(releitura) != len(silver):
        raise RuntimeError(
            "Quantidade de linhas mudou após gravação do Parquet."
        )

    print()
    print(f"Arquivo: {OUTPUT_FILE}")
    print(f"Linhas: {len(silver):,}")
    print(
        "Anos: "
        + ", ".join(
            str(ano)
            for ano in sorted(
                silver["ANO"].unique()
            )
        )
    )
    print(
        f"UFs: {silver['UF'].nunique()}"
    )
    print(
        "Etapas: "
        + ", ".join(
            sorted(
                silver["ETAPA"].unique()
            )
        )
    )
    print(
        "Disciplinas: "
        + ", ".join(
            sorted(
                silver["DISCIPLINA"].unique()
            )
        )
    )
    print(
        f"Rede canônica: {', '.join(sorted(silver['REDE'].unique()))}"
    )
    print(
        f"Valores ausentes: {int(silver['PROFICIENCIA'].isna().sum())}"
    )
    print()
    print(
        "SILVER DO SAEB GERADA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
