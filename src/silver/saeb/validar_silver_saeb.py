from pathlib import Path

import pandas as pd


BRONZE_DIR = Path("data/bronze/saeb")
SILVER_FILE = Path(
    "data/silver/saeb/saeb_2007_2023.parquet"
)

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
    n = numero(
        valor
    )

    if n is None:
        return None

    return int(
        n
    )


def colunas_origem(df):
    return [
        coluna
        for coluna in df.columns
        if str(coluna).startswith("col_")
    ]


def indice_cabecalho(df):
    valores = (
        df["_indice_cabecalho_origem"]
        .dropna()
        .unique()
        .tolist()
    )

    if len(valores) != 1:
        raise RuntimeError(
            "Bronze sem índice de cabeçalho único."
        )

    return int(
        valores[0]
    )


def mapa_cabecalho(df):
    indice = indice_cabecalho(
        df
    )

    linha = df.iloc[
        indice
    ]

    mapa = {}

    for coluna in colunas_origem(
        df
    ):
        valor = texto(
            linha[coluna]
        )

        if valor:
            mapa[
                valor
            ] = coluna

    return mapa


def dados_fonte(df):
    indice = indice_cabecalho(
        df
    )

    return df[
        df["_linha_origem"]
        > indice + 1
    ].copy()


def coluna(mapa, variavel):
    if variavel not in mapa:
        raise RuntimeError(
            f"Variável {variavel!r} ausente."
        )

    return mapa[
        variavel
    ]


def obter_uf(linha, mapa):
    for chave in [
        "CO_UF",
        "ID_UF",
    ]:
        if chave in mapa:
            codigo = inteiro(
                linha[
                    mapa[chave]
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
            return UF_NOME_SIGLA.get(
                remover_acentos(
                    nome
                ).upper()
            )

    return None


def obter_uf_por_nome(valor):
    nome = texto(
        valor
    )

    if not nome:
        return None

    return UF_NOME_SIGLA.get(
        remover_acentos(
            nome
        ).upper()
    )


def extrair_esperados_2007_2009(
    ano,
    df,
):
    mapa = mapa_cabecalho(
        df
    )

    dados = dados_fonte(
        df
    )

    rede_col = coluna(
        mapa,
        "DEPENDENCIA_ADM",
    )
    loc_col = coluna(
        mapa,
        "LOCALIZACAO",
    )
    cap_col = coluna(
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
            origem_col = coluna(
                mapa,
                variavel,
            )

            registros.append(
                {
                    "ANO": ano,
                    "UF": uf,
                    "ETAPA": etapa,
                    "REDE": "PUBLICA",
                    "DISCIPLINA": disciplina,
                    "PROFICIENCIA_ESPERADA": round(
                        numero(
                            linha[
                                origem_col
                            ]
                        ),
                        2,
                    ),
                    "REDE_ORIGEM_ESPERADA": texto(
                        linha[rede_col]
                    ),
                    "LOCALIZACAO_ORIGEM_ESPERADA": texto(
                        linha[loc_col]
                    ),
                    "CAPITAL_ORIGEM_ESPERADA": texto(
                        linha[cap_col]
                    ),
                    "ARQUIVO_ORIGEM_ESPERADO": linha[
                        "_arquivo_origem"
                    ],
                    "ABA_ORIGEM_ESPERADA": linha[
                        "_aba_origem"
                    ],
                    "LINHA_ORIGEM_BRONZE_ESPERADA": inteiro(
                        linha[
                            "_linha_origem"
                        ]
                    ),
                    "COLUNA_ORIGEM_ESPERADA": origem_col,
                    "GRANULARIDADE_ORIGEM_ESPERADA": linha[
                        "_granularidade_origem"
                    ],
                }
            )

    return registros


def extrair_esperados_2011(
    df
):
    mapa = mapa_cabecalho(
        df
    )

    dados = dados_fonte(
        df
    )

    serie_col = coluna(
        mapa,
        "ID_SERIE",
    )
    rede_col = coluna(
        mapa,
        "ID_TIPO_REDE",
    )
    loc_col = coluna(
        mapa,
        "ID_LOCALIZACAO",
    )
    cap_col = coluna(
        mapa,
        "ID_CAPITAL",
    )

    registros = []

    for etapa, serie in {
        "ANOS_INICIAIS": 5,
        "ANOS_FINAIS": 9,
    }.items():
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
                origem_col = coluna(
                    mapa,
                    variavel,
                )

                registros.append(
                    {
                        "ANO": 2011,
                        "UF": uf,
                        "ETAPA": etapa,
                        "REDE": "PUBLICA",
                        "DISCIPLINA": disciplina,
                        "PROFICIENCIA_ESPERADA": round(
                            numero(
                                linha[
                                    origem_col
                                ]
                            ),
                            2,
                        ),
                        "REDE_ORIGEM_ESPERADA": texto(
                            linha[rede_col]
                        ),
                        "LOCALIZACAO_ORIGEM_ESPERADA": texto(
                            linha[loc_col]
                        ),
                        "CAPITAL_ORIGEM_ESPERADA": texto(
                            linha[cap_col]
                        ),
                        "ARQUIVO_ORIGEM_ESPERADO": linha[
                            "_arquivo_origem"
                        ],
                        "ABA_ORIGEM_ESPERADA": linha[
                            "_aba_origem"
                        ],
                        "LINHA_ORIGEM_BRONZE_ESPERADA": inteiro(
                            linha[
                                "_linha_origem"
                            ]
                        ),
                        "COLUNA_ORIGEM_ESPERADA": origem_col,
                        "GRANULARIDADE_ORIGEM_ESPERADA": linha[
                            "_granularidade_origem"
                        ],
                    }
                )

    return registros


def extrair_esperados_2013_2015(
    ano,
    df,
):
    """
    Referência independente para as fontes hierárquicas de 2013 e 2015.
    A estrutura física foi confirmada pela auditoria da Bronze e não
    depende das funções do transformador.
    """
    necessarias = {
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
        necessarias.difference(
            df.columns
        )
    )

    if faltantes:
        raise RuntimeError(
            f"SAEB {ano}: colunas auditadas ausentes: {faltantes}"
        )

    indice = indice_cabecalho(
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
        ), origem_col in metricas.items():
            valor = numero(
                linha[
                    origem_col
                ]
            )

            if ano == 2015 and valor == 0:
                valor = None

            registros.append(
                {
                    "ANO": ano,
                    "UF": uf,
                    "ETAPA": etapa,
                    "REDE": "PUBLICA",
                    "DISCIPLINA": disciplina,
                    "PROFICIENCIA_ESPERADA": (
                        round(
                            valor,
                            2,
                        )
                        if valor is not None
                        else None
                    ),
                    "REDE_ORIGEM_ESPERADA": texto(
                        linha["col_002"]
                    ),
                    "LOCALIZACAO_ORIGEM_ESPERADA": texto(
                        linha["col_003"]
                    ),
                    "CAPITAL_ORIGEM_ESPERADA": texto(
                        linha["col_004"]
                    ),
                    "ARQUIVO_ORIGEM_ESPERADO": linha[
                        "_arquivo_origem"
                    ],
                    "ABA_ORIGEM_ESPERADA": linha[
                        "_aba_origem"
                    ],
                    "LINHA_ORIGEM_BRONZE_ESPERADA": inteiro(
                        linha[
                            "_linha_origem"
                        ]
                    ),
                    "COLUNA_ORIGEM_ESPERADA": origem_col,
                    "GRANULARIDADE_ORIGEM_ESPERADA": linha[
                        "_granularidade_origem"
                    ],
                }
            )

    return registros


def extrair_esperados_2013_2023(
    ano,
    df,
):
    mapa = mapa_cabecalho(
        df
    )

    dados = dados_fonte(
        df
    )

    rede_col = coluna(
        mapa,
        "DEPENDENCIA_ADM",
    )
    loc_col = coluna(
        mapa,
        "LOCALIZACAO",
    )
    cap_col = coluna(
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
            origem_col = coluna(
                mapa,
                variavel,
            )

            valor = numero(
                linha[
                    origem_col
                ]
            )

            if ano == 2015 and valor == 0:
                valor = None

            registros.append(
                {
                    "ANO": ano,
                    "UF": uf,
                    "ETAPA": etapa,
                    "REDE": "PUBLICA",
                    "DISCIPLINA": disciplina,
                    "PROFICIENCIA_ESPERADA": (
                        round(
                            valor,
                            2,
                        )
                        if valor is not None
                        else None
                    ),
                    "REDE_ORIGEM_ESPERADA": texto(
                        linha[rede_col]
                    ),
                    "LOCALIZACAO_ORIGEM_ESPERADA": texto(
                        linha[loc_col]
                    ),
                    "CAPITAL_ORIGEM_ESPERADA": texto(
                        linha[cap_col]
                    ),
                    "ARQUIVO_ORIGEM_ESPERADO": linha[
                        "_arquivo_origem"
                    ],
                    "ABA_ORIGEM_ESPERADA": linha[
                        "_aba_origem"
                    ],
                    "LINHA_ORIGEM_BRONZE_ESPERADA": inteiro(
                        linha[
                            "_linha_origem"
                        ]
                    ),
                    "COLUNA_ORIGEM_ESPERADA": origem_col,
                    "GRANULARIDADE_ORIGEM_ESPERADA": linha[
                        "_granularidade_origem"
                    ],
                }
            )

    return registros


def construir_referencia_bronze():
    registros = []

    for ano in ANOS:
        arquivo = ARQUIVOS[
            ano
        ]

        if not arquivo.exists():
            raise FileNotFoundError(
                f"Bronze ausente para {ano}: {arquivo}"
            )

        df = pd.read_parquet(
            arquivo
        )

        if ano in {
            2007,
            2009,
        }:
            registros.extend(
                extrair_esperados_2007_2009(
                    ano,
                    df,
                )
            )

        elif ano == 2011:
            registros.extend(
                extrair_esperados_2011(
                    df
                )
            )

        elif ano in {
            2013,
            2015,
        }:
            registros.extend(
                extrair_esperados_2013_2015(
                    ano,
                    df,
                )
            )

        else:
            registros.extend(
                extrair_esperados_2013_2023(
                    ano,
                    df,
                )
            )

    return pd.DataFrame(
        registros
    )


def validar_estrutura(silver):
    esperado = (
        len(ANOS)
        * 27
        * 2
        * 2
    )

    if len(silver) != esperado:
        raise RuntimeError(
            f"Linhas Silver={len(silver)}; esperado={esperado}."
        )

    if set(silver["ANO"]) != set(ANOS):
        raise RuntimeError(
            "Anos da Silver diferentes do esperado."
        )

    if set(silver["UF"]) != UFS:
        raise RuntimeError(
            "UFs da Silver diferentes das 27 UFs."
        )

    if set(silver["ETAPA"]) != {
        "ANOS_INICIAIS",
        "ANOS_FINAIS",
    }:
        raise RuntimeError(
            "Etapas inválidas."
        )

    if set(silver["DISCIPLINA"]) != {
        "LP",
        "MT",
    }:
        raise RuntimeError(
            "Disciplinas inválidas."
        )

    if set(silver["REDE"]) != {
        "PUBLICA",
    }:
        raise RuntimeError(
            "Rede canônica inválida."
        )

    chave = [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "DISCIPLINA",
    ]

    if silver.duplicated(
        subset=chave
    ).any():
        raise RuntimeError(
            "Há duplicidade no grão analítico."
        )

    if silver[
        "PROFICIENCIA"
    ].isna().any():
        raise RuntimeError(
            "Há proficiência ausente."
        )

    fora = silver[
        ~silver[
            "PROFICIENCIA"
        ].between(
            0,
            500,
            inclusive="both",
        )
    ]

    if not fora.empty:
        raise RuntimeError(
            "Há proficiência fora do domínio plausível 0–500."
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
        por_ano_etapa == 27
    ).all():
        raise RuntimeError(
            "Algum ano/etapa não possui 27 UFs."
        )


def validar_contra_bronze(
    silver,
    referencia,
):
    chave = [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "DISCIPLINA",
    ]

    combinado = silver.merge(
        referencia,
        on=chave,
        how="outer",
        validate="one_to_one",
        indicator=True,
    )

    if not (
        combinado["_merge"] == "both"
    ).all():
        problemas = combinado[
            combinado["_merge"] != "both"
        ][
            chave
            + ["_merge"]
        ]

        raise RuntimeError(
            "Silver e referência Bronze não possuem o mesmo grão:\n"
            + problemas.head(
                20
            ).to_string(
                index=False
            )
        )

    comparacoes = {
        "PROFICIENCIA": "PROFICIENCIA_ESPERADA",
        "REDE_ORIGEM": "REDE_ORIGEM_ESPERADA",
        "LOCALIZACAO_ORIGEM": "LOCALIZACAO_ORIGEM_ESPERADA",
        "CAPITAL_ORIGEM": "CAPITAL_ORIGEM_ESPERADA",
        "ARQUIVO_ORIGEM": "ARQUIVO_ORIGEM_ESPERADO",
        "ABA_ORIGEM": "ABA_ORIGEM_ESPERADA",
        "LINHA_ORIGEM_BRONZE": "LINHA_ORIGEM_BRONZE_ESPERADA",
        "COLUNA_ORIGEM": "COLUNA_ORIGEM_ESPERADA",
        "GRANULARIDADE_ORIGEM": "GRANULARIDADE_ORIGEM_ESPERADA",
    }

    divergencias = []

    for atual, esperado in comparacoes.items():
        esquerda = combinado[
            atual
        ]

        direita = combinado[
            esperado
        ]

        if atual == "PROFICIENCIA":
            iguais = (
                pd.to_numeric(
                    esquerda,
                    errors="coerce",
                )
                .round(2)
                .eq(
                    pd.to_numeric(
                        direita,
                        errors="coerce",
                    ).round(2)
                )
            )
        else:
            iguais = (
                esquerda
                .astype("string")
                .fillna("__AUSENTE__")
                .eq(
                    direita
                    .astype("string")
                    .fillna("__AUSENTE__")
                )
            )

        if not iguais.all():
            problema = combinado.loc[
                ~iguais,
                chave
                + [
                    atual,
                    esperado,
                ],
            ].copy()

            problema[
                "CAMPO"
            ] = atual

            divergencias.append(
                problema.head(
                    20
                )
            )

    if divergencias:
        amostra = pd.concat(
            divergencias,
            ignore_index=True,
        )

        raise RuntimeError(
            "Foram encontradas divergências Silver ↔ Bronze:\n"
            + amostra.head(
                30
            ).to_string(
                index=False
            )
        )

    return len(
        combinado
    )


def main():
    print("=" * 110)
    print(
        "VALIDAÇÃO INDEPENDENTE — SILVER SAEB 2007–2023"
    )
    print("=" * 110)
    print()

    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Silver ausente: {SILVER_FILE}"
        )

    print(
        "1/4 Lendo Silver..."
    )
    silver = pd.read_parquet(
        SILVER_FILE
    )

    print(
        "2/4 Validando estrutura e grão..."
    )
    validar_estrutura(
        silver
    )

    print(
        "3/4 Reconstruindo referência diretamente das Bronzes..."
    )
    referencia = construir_referencia_bronze()

    print(
        "4/4 Comparando valores e rastreabilidade Silver ↔ Bronze..."
    )
    comparados = validar_contra_bronze(
        silver,
        referencia,
    )

    print()
    print(
        f"Arquivo Silver: {SILVER_FILE.name}"
    )
    print(
        f"Linhas: {len(silver):,}"
    )
    print(
        "Anos: 9/9 "
        "(2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023)"
    )
    print(
        "UFs por ano/etapa: 27"
    )
    print(
        "Etapas: ANOS_INICIAIS, ANOS_FINAIS"
    )
    print(
        "Disciplinas: LP, MT"
    )
    print(
        "Rede: PUBLICA"
    )
    print(
        "Grão analítico único: OK"
    )
    print(
        "Domínio plausível da proficiência 0–500: OK"
    )
    print(
        "Regra específica de zero do Saeb 2015: OK"
    )
    print(
        "2007/2009 preservam agregado de origem Total - Estadual e Municipal: OK"
    )
    print(
        "2013–2023 preservam agregado oficial Total - Federal, Estadual e Municipal: OK"
    )
    print(
        "2023 usa a Bronze oficial agregada de UF, não média de escolas por NU_PRESENTES: OK"
    )
    print(
        f"Registros comparados diretamente com as Bronzes: {comparados:,}"
    )
    print(
        "Rastreabilidade arquivo/aba/linha/coluna/granularidade: OK"
    )
    print()
    print(
        "SILVER DO SAEB: OK"
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
