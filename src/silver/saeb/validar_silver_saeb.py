from pathlib import Path

import numpy as np
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


def linha_cabecalho(df, numero_linha):
    linhas = df.loc[df["_linha_origem"].eq(numero_linha), colunas_origem(df)]
    if len(linhas) != 1:
        raise RuntimeError(f"Linha física de cabeçalho ausente ou ambígua: {numero_linha}.")
    return linhas.iloc[0]


def mapa_cabecalho(df):
    indice = indice_cabecalho(
        df
    )

    linha = linha_cabecalho(df, indice + 1)

    mapa = {}

    for coluna in colunas_origem(
        df
    ):
        valor = texto(
            linha[coluna]
        )

        if valor:
            if valor in mapa:
                raise RuntimeError(f"Cabeçalho ambíguo: {valor!r}.")
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
    # O código e a identificação textual estão publicados na mesma linha.
    if "ID_UF" in mapa:
        codigo = linha[coluna(mapa, "ID_UF")]
        sigla = texto(linha[coluna(mapa, "SIGLA_UF")])
    else:
        codigo = linha[coluna(mapa, "CO_UF")]
        sigla = obter_uf_por_nome(linha[coluna(mapa, "NO_UF")])
    if sigla not in UFS or UF_CODIGO_SIGLA.get(inteiro(codigo)) != sigla:
        raise RuntimeError(f"Identificações da UF divergentes na Bronze: {codigo!r}, {sigla!r}.")
    return sigla


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


def rede_publica(rotulos, ano):
    # A composição publicada muda em 2013. A palavra "Total" sozinha
    # também está presente no agregado que inclui a rede privada.
    componentes = {"Estadual", "Municipal"}
    if ano >= 2013:
        componentes.add("Federal")

    def corresponde(rotulo):
        prefixo, separador, nomes = str(rotulo).strip().partition(" - ")
        return (prefixo == "Total" and bool(separador)
                and set(nomes.replace(" e ", ", ").split(", ")) == componentes)

    return rotulos.map(corresponde)


def disciplinas_tecnicas(ano):
    series = (4, 8) if ano <= 2009 else (5, 9)
    return {
        (etapa, disciplina): f"MEDIA_{serie}_{disciplina}"
        for etapa, serie in zip(("ANOS_INICIAIS", "ANOS_FINAIS"), series)
        for disciplina in ("LP", "MT")
    }


def codigos_2011(arquivo=Path("data/raw/saeb/Dicionario_SAEB_2011.xlsx")):
    # Na aba TS_RESULTADO_UF as linhas de continuação pertencem à última variável.
    dicionario = pd.read_excel(
        arquivo, sheet_name="TS_RESULTADO_UF",
        usecols=[0, 4], header=None, names=["variavel", "categoria"],
    )
    dicionario["variavel"] = dicionario["variavel"].ffill()

    def codigo(variavel, descricao):
        categorias = dicionario.loc[dicionario.variavel.eq(variavel), "categoria"].dropna()
        encontrados = [item.partition(" - ")[0] for item in categorias
                       if item.partition(" - ")[2] == descricao]
        if len(encontrados) != 1:
            raise RuntimeError(f"Dicionário SAEB 2011: {variavel}/{descricao} ausente ou ambíguo.")
        return int(encontrados[0])

    return {
        "ANOS_INICIAIS": codigo("ID_SERIE", "4ª série/5º ano Ensino Fundamental"),
        "ANOS_FINAIS": codigo("ID_SERIE", "8ª série/9º ano Ensino Fundamental"),
        "rede": codigo("ID_TIPO_REDE", "Pública"),
        "localizacao": codigo("ID_LOCALIZACAO", "Todas"),
        "capital": codigo("ID_CAPITAL", "Todas"),
    }


def cabecalho_hierarquico(df):
    inicio = indice_cabecalho(df) + 1
    grupos = linha_cabecalho(df, inicio)
    titulos = linha_cabecalho(df, inicio + 1)
    etapas = titulos.ffill()
    disciplinas = linha_cabecalho(df, inicio + 2)

    def unica(mascara, rotulo):
        encontradas = grupos.index[mascara.fillna(False)]
        if len(encontradas) != 1:
            raise RuntimeError(f"Cabeçalho hierárquico ausente ou ambíguo: {rotulo}.")
        return encontradas[0]

    dimensoes = {nome: unica(grupos.eq(nome), nome)
                 for nome in ("UF", "REDE", "LOCALIZAÇÃO", "CAPITAL")}
    # Cada etapa começa sob seu próprio título de médias na linha superior.
    medias = grupos.fillna("").eq("MÉDIAS DE PROFICIÊNCIA")
    proficiencia = medias.where(titulos.notna()).ffill().fillna(False)
    metricas = {}
    for etapa, titulo in [("ANOS_INICIAIS", "ANOS INICIAIS - 5º ANO"),
                          ("ANOS_FINAIS", "ANOS FINAIS - 9º ANO")]:
        for disciplina, nome in [("LP", "LÍNGUA PORTUGUESA"), ("MT", "MATEMÁTICA")]:
            metricas[etapa, disciplina] = unica(
                proficiencia & etapas.fillna("").eq(titulo) & disciplinas.fillna("").eq(nome),
                f"{titulo}/{nome}"
            )
    return dimensoes, metricas


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
        rede_publica(dados[rede_col], ano)
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

    metricas = disciplinas_tecnicas(ano)

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
                    "PROFICIENCIA_ESPERADA": numero(linha[origem_col]),
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

    codigos = codigos_2011()
    for etapa in ("ANOS_INICIAIS", "ANOS_FINAIS"):
        serie = codigos[etapa]
        alvo = dados[
            (
                dados[serie_col]
                .map(inteiro)
                == serie
            )
            & (
                dados[rede_col]
                .map(inteiro)
                == codigos["rede"]
            )
            & (
                dados[loc_col]
                .map(inteiro)
                == codigos["localizacao"]
            )
            & (
                dados[cap_col]
                .map(inteiro)
                == codigos["capital"]
            )
        ].copy()

        for _, linha in alvo.iterrows():
            uf = obter_uf(
                linha,
                mapa,
            )

            if uf not in UFS:
                continue

            for disciplina in ("LP", "MT"):
                variavel = f"MEDIA_{disciplina}"
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
                        "PROFICIENCIA_ESPERADA": numero(linha[origem_col]),
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
    dimensoes, metricas = cabecalho_hierarquico(df)
    dados = df.loc[df["_linha_origem"] >= indice_cabecalho(df) + 4]
    alvo = dados.loc[
        rede_publica(dados[dimensoes["REDE"]], ano)
        & dados[dimensoes["LOCALIZAÇÃO"]].str.strip().eq("Total")
        & dados[dimensoes["CAPITAL"]].str.strip().eq("Total")
    ]

    registros = []

    for _, linha in alvo.iterrows():
        uf = obter_uf_por_nome(
            linha[dimensoes["UF"]]
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
                    "PROFICIENCIA_ESPERADA": valor,
                    "REDE_ORIGEM_ESPERADA": texto(
                        linha[dimensoes["REDE"]]
                    ),
                    "LOCALIZACAO_ORIGEM_ESPERADA": texto(
                        linha[dimensoes["LOCALIZAÇÃO"]]
                    ),
                    "CAPITAL_ORIGEM_ESPERADA": texto(
                        linha[dimensoes["CAPITAL"]]
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
        rede_publica(dados[rede_col], ano)
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

    metricas = disciplinas_tecnicas(ano)

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
                    "PROFICIENCIA_ESPERADA": valor,
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

        if not df["_ano_referencia"].eq(ano).fillna(False).all():
            raise RuntimeError(f"SAEB {ano}: edição da Bronze divergente.")
        if not df["_granularidade_origem"].eq("UF").fillna(False).all():
            raise RuntimeError(f"SAEB {ano}: esperada a publicação agregada por UF.")
        if ano in (2007, 2009, 2011, 2023):
            variavel = "ID_SAEB" if ano == 2011 else "ANO_SAEB"
            campo = coluna(mapa_cabecalho(df), variavel)
            if not dados_fonte(df)[campo].eq(str(ano)).fillna(False).all():
                raise RuntimeError(f"SAEB {ano}: ano publicado em {variavel} divergente.")

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
            observado = pd.to_numeric(esquerda, errors="raise").to_numpy(dtype=float)
            publicado = pd.to_numeric(direita, errors="raise").to_numpy(dtype=float)
            # As células das planilhas podem diferir do decimal publicado em um ULP.
            iguais = np.isclose(observado, publicado, rtol=0, atol=np.spacing(publicado))
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
