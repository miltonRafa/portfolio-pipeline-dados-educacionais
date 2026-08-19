from pathlib import Path

import pandas as pd


BRONZE_FILE = Path(
    "data/bronze/pnd/pnd_2025.parquet"
)

SILVER_DIR = Path(
    "data/silver/pnd"
)

OUTPUT_FILE = SILVER_DIR / "pnd_2025.parquet"

TOTAL_DADOS_ESPERADO = 1_087_359
TOTAL_RESULTADOS_COMPLETOS_ESPERADO = 759_152
TOTAL_POPULACAO_ANALITICA_ESPERADO = 759_140
TOTAL_555_SEM_RESULTADO_ESPERADO = 966
TOTAL_888_COM_RESULTADO_ESPERADO = 12

UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF",
    "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
    "RO", "RR", "SC", "SP", "SE", "TO",
}

# Categorias oficiais do CO_GRUPO registradas no
# Dicionário de Variáveis da PND 2025.
AREAS = {
    702: "MATEMÁTICA (LICENCIATURA)",
    904: "LETRAS - PORTUGUÊS (LICENCIATURA)",
    905: "LETRAS - PORTUGUÊS E INGLÊS (LICENCIATURA)",
    906: "LETRAS - PORTUGUÊS E ESPANHOL (LICENCIATURA)",
    1402: "FÍSICA (LICENCIATURA)",
    1502: "QUÍMICA (LICENCIATURA)",
    1602: "CIÊNCIAS BIOLÓGICAS (LICENCIATURA)",
    2001: "PEDAGOGIA (LICENCIATURA)",
    2402: "HISTÓRIA (LICENCIATURA)",
    2501: "ARTES VISUAIS (LICENCIATURA)",
    3002: "GEOGRAFIA (LICENCIATURA)",
    3202: "FILOSOFIA (LICENCIATURA)",
    3502: "EDUCAÇÃO FÍSICA (LICENCIATURA)",
    4005: "CIÊNCIA DA COMPUTAÇÃO (LICENCIATURA)",
    4301: "MÚSICA (LICENCIATURA)",
    5402: "CIÊNCIAS SOCIAIS (LICENCIATURA)",
    6407: "LETRAS - INGLÊS (LICENCIATURA)",
}

# Ordem física confirmada no arquivo principal da PND.
MAPA = {
    "NU_ANO": "col_001",
    "CO_GRUPO": "col_002",
    "CO_MUNICIPIO_PROVA": "col_003",
    "SG_UF_MUNICIPIO_PROVA": "col_004",
    "TP_INSCRICAO_PND": "col_005",
    "IN_REAPLICACAO": "col_006",
    "CO_CADERNO": "col_007",
    "TP_PRES": "col_011",
    "TP_SIT_DISC": "col_012",
    "PROFICIENCIA": "col_013",
    "NT_OBJ": "col_014",
    "NT_DIS": "col_015",
    "NT_GER": "col_016",
    "QT_ACERTOS": "col_017",
}

CAMPOS_RESULTADO = [
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
]

COLUNAS_LEITURA = list(
    dict.fromkeys(
        [
            *MAPA.values(),
            "_arquivo_origem",
            "_granularidade_origem",
            "_linha_origem",
            "_indice_cabecalho_origem",
        ]
    )
)


def texto_limpo(serie):
    return (
        serie
        .astype("string")
        .str.strip()
    )


def mascara_ausente(serie):
    texto = texto_limpo(
        serie
    )

    return (
        texto.isna()
        | texto.eq("")
        | texto.str.upper().eq("NA")
    )


def serie_numerica(serie):
    texto = texto_limpo(
        serie
    )

    texto = texto.mask(
        mascara_ausente(
            serie
        )
    )

    texto = texto.str.replace(
        ",",
        ".",
        regex=False,
    )

    return pd.to_numeric(
        texto,
        errors="coerce",
    )


def serie_inteira(serie, nome):
    numerica = serie_numerica(
        serie
    )

    validos = numerica.dropna()

    nao_inteiros = (
        validos
        .mod(1)
        .ne(0)
    )

    if nao_inteiros.any():
        exemplos = (
            validos[
                nao_inteiros
            ]
            .head(10)
            .tolist()
        )

        raise RuntimeError(
            f"{nome}: foram encontrados valores não inteiros: {exemplos}"
        )

    return numerica.astype(
        "Int64"
    )


def validar_estrutura_bronze(df):
    faltantes = sorted(
        set(COLUNAS_LEITURA)
        .difference(
            df.columns
        )
    )

    if faltantes:
        raise RuntimeError(
            f"Colunas Bronze ausentes: {faltantes}"
        )

    indices = (
        df[
            "_indice_cabecalho_origem"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    if indices != [0]:
        raise RuntimeError(
            "_indice_cabecalho_origem deveria ser 0 para a PND 2025; "
            f"encontrado={indices}"
        )

    if df.empty:
        raise RuntimeError(
            "A Bronze da PND está vazia."
        )

    cabecalho = df.loc[
        df["_linha_origem"] == 1
    ]

    if len(cabecalho) != 1:
        raise RuntimeError(
            "A linha física de cabeçalho da PND não foi encontrada de forma única."
        )

    linha = cabecalho.iloc[0]

    divergencias = []

    for nome, coluna in MAPA.items():
        atual = str(
            linha[coluna]
        ).strip()

        if atual != nome:
            divergencias.append(
                f"{coluna}: esperado={nome!r}; atual={atual!r}"
            )

    if divergencias:
        raise RuntimeError(
            "Cabeçalho da Bronze diferente da estrutura auditada:\n"
            + "\n".join(
                divergencias
            )
        )


def diagnosticar_populacao(dados):
    mascaras_resultado = [
        ~mascara_ausente(
            dados[
                MAPA[campo]
            ]
        )
        for campo in CAMPOS_RESULTADO
    ]

    todos_resultados = mascaras_resultado[0].copy()
    todos_ausentes = ~mascaras_resultado[0].copy()

    for mascara in mascaras_resultado[1:]:
        todos_resultados &= mascara
        todos_ausentes &= ~mascara

    parcialmente_preenchidos = ~(
        todos_resultados
        | todos_ausentes
    )

    tp_pres = serie_inteira(
        dados[
            MAPA["TP_PRES"]
        ],
        "TP_PRES",
    )

    diagnostico = {
        "total_dados": int(
            len(dados)
        ),
        "todos_resultados": int(
            todos_resultados.sum()
        ),
        "todos_ausentes": int(
            todos_ausentes.sum()
        ),
        "parciais": int(
            parcialmente_preenchidos.sum()
        ),
        "pres_555_com_resultado": int(
            (
                tp_pres.eq(555)
                & todos_resultados
            ).sum()
        ),
        "pres_555_sem_resultado": int(
            (
                tp_pres.eq(555)
                & ~todos_resultados
            ).sum()
        ),
        "pres_888_com_resultado": int(
            (
                tp_pres.eq(888)
                & todos_resultados
            ).sum()
        ),
    }

    return (
        diagnostico,
        todos_resultados,
        tp_pres,
    )


def validar_diagnostico(
    diagnostico,
):
    esperado = {
        "total_dados": TOTAL_DADOS_ESPERADO,
        "todos_resultados": TOTAL_RESULTADOS_COMPLETOS_ESPERADO,
        "parciais": 0,
        "pres_555_com_resultado": TOTAL_POPULACAO_ANALITICA_ESPERADO,
        "pres_555_sem_resultado": TOTAL_555_SEM_RESULTADO_ESPERADO,
        "pres_888_com_resultado": TOTAL_888_COM_RESULTADO_ESPERADO,
    }

    divergencias = {}

    for chave, valor_esperado in esperado.items():
        atual = diagnostico[
            chave
        ]

        if atual != valor_esperado:
            divergencias[
                chave
            ] = {
                "esperado": valor_esperado,
                "atual": atual,
            }

    if divergencias:
        raise RuntimeError(
            "A população da Bronze mudou em relação à auditoria documentada:\n"
            + "\n".join(
                (
                    f"{chave}: "
                    f"esperado={valores['esperado']:,}; "
                    f"atual={valores['atual']:,}"
                )
                for chave, valores in divergencias.items()
            )
        )


def construir_silver(
    dados,
    todos_resultados,
    tp_pres,
):
    mascara_populacao = (
        tp_pres.eq(555)
        & todos_resultados
    )

    origem = dados.loc[
        mascara_populacao
    ].copy()

    silver = pd.DataFrame(
        index=origem.index
    )

    silver["ANO"] = serie_inteira(
        origem[
            MAPA["NU_ANO"]
        ],
        "NU_ANO",
    )

    silver["CO_GRUPO"] = serie_inteira(
        origem[
            MAPA["CO_GRUPO"]
        ],
        "CO_GRUPO",
    )

    silver["AREA_PROVA"] = silver[
        "CO_GRUPO"
    ].map(
        AREAS
    ).astype(
        "string"
    )

    silver[
        "CO_MUNICIPIO_PROVA"
    ] = serie_inteira(
        origem[
            MAPA["CO_MUNICIPIO_PROVA"]
        ],
        "CO_MUNICIPIO_PROVA",
    )

    silver["UF_PROVA"] = (
        texto_limpo(
            origem[
                MAPA["SG_UF_MUNICIPIO_PROVA"]
            ]
        )
        .str.upper()
    )

    silver[
        "TP_INSCRICAO_PND"
    ] = serie_inteira(
        origem[
            MAPA["TP_INSCRICAO_PND"]
        ],
        "TP_INSCRICAO_PND",
    )

    silver[
        "IN_REAPLICACAO"
    ] = serie_inteira(
        origem[
            MAPA["IN_REAPLICACAO"]
        ],
        "IN_REAPLICACAO",
    )

    silver["CO_CADERNO"] = serie_inteira(
        origem[
            MAPA["CO_CADERNO"]
        ],
        "CO_CADERNO",
    )

    silver["TP_PRES"] = serie_inteira(
        origem[
            MAPA["TP_PRES"]
        ],
        "TP_PRES",
    )

    silver[
        "TP_SIT_DISC"
    ] = serie_inteira(
        origem[
            MAPA["TP_SIT_DISC"]
        ],
        "TP_SIT_DISC",
    )

    for campo in [
        "PROFICIENCIA",
        "NT_OBJ",
        "NT_DIS",
        "NT_GER",
    ]:
        silver[campo] = serie_numerica(
            origem[
                MAPA[campo]
            ]
        ).astype(
            "Float64"
        )

    silver[
        "QT_ACERTOS"
    ] = serie_inteira(
        origem[
            MAPA["QT_ACERTOS"]
        ],
        "QT_ACERTOS",
    )

    silver[
        "ARQUIVO_ORIGEM"
    ] = texto_limpo(
        origem[
            "_arquivo_origem"
        ]
    )

    silver[
        "LINHA_ORIGEM_BRONZE"
    ] = (
        pd.to_numeric(
            origem[
                "_linha_origem"
            ],
            errors="raise",
        )
        .astype(
            "int64"
        )
    )

    silver[
        "GRANULARIDADE_ORIGEM"
    ] = texto_limpo(
        origem[
            "_granularidade_origem"
        ]
    )

    return silver.reset_index(
        drop=True
    )


def validar_silver_antes_gravacao(
    silver,
):
    if len(silver) != TOTAL_POPULACAO_ANALITICA_ESPERADO:
        raise RuntimeError(
            f"Silver com {len(silver):,} linhas; "
            f"esperado={TOTAL_POPULACAO_ANALITICA_ESPERADO:,}."
        )

    if set(
        silver[
            "ANO"
        ].dropna().astype(int)
    ) != {2025}:
        raise RuntimeError(
            "ANO da Silver da PND deveria conter apenas 2025."
        )

    if set(
        silver[
            "UF_PROVA"
        ].dropna()
    ) != UFS:
        faltantes = sorted(
            UFS
            - set(
                silver[
                    "UF_PROVA"
                ].dropna()
            )
        )

        extras = sorted(
            set(
                silver[
                    "UF_PROVA"
                ].dropna()
            )
            - UFS
        )

        raise RuntimeError(
            "Conjunto de UFs da população analítica é diferente das 27 UFs.\n"
            f"Faltantes={faltantes}\n"
            f"Extras={extras}"
        )

    if not silver[
        "TP_PRES"
    ].eq(555).all():
        raise RuntimeError(
            "A Silver contém TP_PRES diferente de 555."
        )

    if silver[
        "AREA_PROVA"
    ].isna().any():
        codigos = sorted(
            silver.loc[
                silver[
                    "AREA_PROVA"
                ].isna(),
                "CO_GRUPO",
            ]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        raise RuntimeError(
            "Há CO_GRUPO sem categoria oficial mapeada: "
            f"{codigos}"
        )

    campos_obrigatorios = [
        "ANO",
        "CO_GRUPO",
        "AREA_PROVA",
        "CO_MUNICIPIO_PROVA",
        "UF_PROVA",
        "TP_INSCRICAO_PND",
        "IN_REAPLICACAO",
        "CO_CADERNO",
        "TP_PRES",
        "TP_SIT_DISC",
        "PROFICIENCIA",
        "NT_OBJ",
        "NT_DIS",
        "NT_GER",
        "QT_ACERTOS",
        "ARQUIVO_ORIGEM",
        "LINHA_ORIGEM_BRONZE",
        "GRANULARIDADE_ORIGEM",
    ]

    ausencias = {
        campo: int(
            silver[
                campo
            ].isna().sum()
        )
        for campo in campos_obrigatorios
        if silver[
            campo
        ].isna().any()
    }

    if ausencias:
        raise RuntimeError(
            f"Campos obrigatórios com ausências: {ausencias}"
        )

    if silver[
        "LINHA_ORIGEM_BRONZE"
    ].duplicated().any():
        raise RuntimeError(
            "LINHA_ORIGEM_BRONZE deveria ser única na Silver da PND."
        )

    granularidades = set(
        silver[
            "GRANULARIDADE_ORIGEM"
        ].dropna()
    )

    if granularidades != {
        "REGISTRO_INDIVIDUAL",
    }:
        raise RuntimeError(
            "Granularidade de origem inesperada: "
            f"{sorted(granularidades)}"
        )

    # Não é aplicado limite inferior arbitrário a PROFICIENCIA,
    # NT_OBJ, NT_DIS ou NT_GER.
    #
    # A fonte preservada e o dicionário utilizado no projeto não
    # documentam, na evidência atualmente disponível, que esses
    # quatro campos devam ser estritamente não negativos. Portanto,
    # a Silver preserva os valores numéricos publicados em vez de
    # rejeitá-los com uma regra de domínio inventada pelo pipeline.
    #
    # QT_ACERTOS é diferente: trata-se de uma contagem de acertos,
    # logo valores negativos seriam semanticamente incompatíveis.
    if (
        silver[
            "QT_ACERTOS"
        ]
        < 0
    ).any():
        exemplos = (
            silver.loc[
                silver[
                    "QT_ACERTOS"
                ] < 0,
                [
                    "LINHA_ORIGEM_BRONZE",
                    "QT_ACERTOS",
                ],
            ]
            .head(10)
            .to_dict(
                orient="records"
            )
        )

        raise RuntimeError(
            "Foram encontrados valores negativos em QT_ACERTOS: "
            f"{exemplos}"
        )



def diagnosticar_resultados_numericos(silver):
    resumo = {}

    for campo in [
        "PROFICIENCIA",
        "NT_OBJ",
        "NT_DIS",
        "NT_GER",
        "QT_ACERTOS",
    ]:
        serie = pd.to_numeric(
            silver[
                campo
            ],
            errors="coerce",
        )

        resumo[
            campo
        ] = {
            "min": float(
                serie.min()
            ),
            "max": float(
                serie.max()
            ),
            "negativos": int(
                (
                    serie < 0
                ).sum()
            ),
        }

    return resumo


def main():
    print("=" * 110)
    print(
        "TRANSFORMAÇÃO SILVER — PND 2025"
    )
    print("=" * 110)
    print()

    if not BRONZE_FILE.exists():
        raise FileNotFoundError(
            f"Bronze não encontrada: {BRONZE_FILE}"
        )

    print(
        "1/5 Lendo colunas necessárias da Bronze..."
    )

    bronze = pd.read_parquet(
        BRONZE_FILE,
        columns=COLUNAS_LEITURA,
    )

    print(
        "2/5 Validando estrutura e cabeçalho..."
    )

    validar_estrutura_bronze(
        bronze
    )

    dados = bronze[
        bronze[
            "_linha_origem"
        ] > 1
    ].copy()

    print(
        "3/5 Reproduzindo o diagnóstico da população..."
    )

    (
        diagnostico,
        todos_resultados,
        tp_pres,
    ) = diagnosticar_populacao(
        dados
    )

    validar_diagnostico(
        diagnostico
    )

    print(
        "4/5 Aplicando população analítica: TP_PRES=555 + cinco resultados completos..."
    )

    silver = construir_silver(
        dados,
        todos_resultados,
        tp_pres,
    )

    validar_silver_antes_gravacao(
        silver
    )

    print(
        "5/5 Gravando Parquet Silver..."
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
            "Quantidade de linhas mudou após a gravação do Parquet."
        )

    print()
    print(
        f"Registros de dados na Bronze: {diagnostico['total_dados']:,}"
    )
    print(
        f"Com os cinco resultados completos: {diagnostico['todos_resultados']:,}"
    )
    print(
        f"Resultados parcialmente preenchidos: {diagnostico['parciais']:,}"
    )
    print(
        f"TP_PRES=555 + resultados completos: {diagnostico['pres_555_com_resultado']:,}"
    )
    print(
        f"TP_PRES=555 sem conjunto completo de resultados: "
        f"{diagnostico['pres_555_sem_resultado']:,}"
    )
    print(
        f"TP_PRES=888 + resultados completos excluídos: "
        f"{diagnostico['pres_888_com_resultado']:,}"
    )
    print()
    print(
        f"Arquivo Silver: {OUTPUT_FILE}"
    )
    print(
        f"Linhas Silver: {len(silver):,}"
    )
    print(
        f"UFs: {silver['UF_PROVA'].nunique()}"
    )
    print(
        f"Áreas da prova: {silver['CO_GRUPO'].nunique()}"
    )
    print(
        f"Municípios de prova: {silver['CO_MUNICIPIO_PROVA'].nunique():,}"
    )
    print(
        f"Valores ausentes nas cinco medidas: "
        f"{int(silver[CAMPOS_RESULTADO].isna().sum().sum()):,}"
    )
    print()

    resumo_numerico = diagnosticar_resultados_numericos(
        silver
    )

    print(
        "DIAGNÓSTICO DOS RESULTADOS NUMÉRICOS"
    )

    for campo, valores in resumo_numerico.items():
        print(
            f"{campo}: "
            f"mín={valores['min']:.6f} | "
            f"máx={valores['max']:.6f} | "
            f"negativos={valores['negativos']:,}"
        )

    print()
    print(
        "Observação: valores negativos em PROFICIENCIA/NT_OBJ/NT_DIS/NT_GER "
        "são preservados quando publicados pela fonte; o pipeline não impõe "
        "limite inferior não documentado."
    )
    print()
    print(
        "SILVER DA PND 2025 GERADA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
