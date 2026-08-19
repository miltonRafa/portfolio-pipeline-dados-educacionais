from pathlib import Path

import numpy as np
import pandas as pd


BRONZE_FILE = Path(
    "data/bronze/pnd/pnd_2025.parquet"
)

SILVER_FILE = Path(
    "data/silver/pnd/pnd_2025.parquet"
)

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

COLUNAS_BRONZE = list(
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

COLUNAS_SILVER = [
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


def texto_limpo(serie):
    return (
        serie
        .astype("string")
        .str.strip()
    )


def ausente(serie):
    texto = texto_limpo(
        serie
    )

    return (
        texto.isna()
        | texto.eq("")
        | texto.str.upper().eq("NA")
    )


def numerico(serie):
    texto = texto_limpo(
        serie
    )

    texto = texto.mask(
        ausente(
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


def inteiro(serie, nome):
    valores = numerico(
        serie
    )

    validos = valores.dropna()

    if (
        validos.mod(1).ne(0)
    ).any():
        raise RuntimeError(
            f"{nome}: valor não inteiro encontrado na Bronze."
        )

    return valores.astype(
        "Int64"
    )


def validar_cabecalho(bronze):
    indices = (
        bronze[
            "_indice_cabecalho_origem"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    if indices != [0]:
        raise RuntimeError(
            "Índice de cabeçalho da Bronze diferente de 0."
        )

    cabecalho = bronze.loc[
        bronze[
            "_linha_origem"
        ] == 1
    ]

    if len(cabecalho) != 1:
        raise RuntimeError(
            "Cabeçalho físico da PND não encontrado de forma única."
        )

    linha = cabecalho.iloc[0]

    for nome, coluna in MAPA.items():
        atual = str(
            linha[
                coluna
            ]
        ).strip()

        if atual != nome:
            raise RuntimeError(
                f"Cabeçalho divergente em {coluna}: "
                f"esperado={nome!r}; atual={atual!r}"
            )


def reconstruir_referencia(bronze):
    dados = bronze.loc[
        bronze[
            "_linha_origem"
        ] > 1
    ].copy()

    if len(dados) != TOTAL_DADOS_ESPERADO:
        raise RuntimeError(
            f"Registros Bronze={len(dados):,}; "
            f"esperado={TOTAL_DADOS_ESPERADO:,}."
        )

    presentes_resultado = [
        ~ausente(
            dados[
                MAPA[campo]
            ]
        )
        for campo in CAMPOS_RESULTADO
    ]

    completos = presentes_resultado[0].copy()
    todos_ausentes = ~presentes_resultado[0].copy()

    for mascara in presentes_resultado[1:]:
        completos &= mascara
        todos_ausentes &= ~mascara

    parciais = ~(
        completos
        | todos_ausentes
    )

    tp_pres = inteiro(
        dados[
            MAPA["TP_PRES"]
        ],
        "TP_PRES",
    )

    contagens = {
        "completos": int(
            completos.sum()
        ),
        "parciais": int(
            parciais.sum()
        ),
        "555_completo": int(
            (
                tp_pres.eq(555)
                & completos
            ).sum()
        ),
        "555_incompleto": int(
            (
                tp_pres.eq(555)
                & ~completos
            ).sum()
        ),
        "888_completo": int(
            (
                tp_pres.eq(888)
                & completos
            ).sum()
        ),
    }

    esperado = {
        "completos": TOTAL_RESULTADOS_COMPLETOS_ESPERADO,
        "parciais": 0,
        "555_completo": TOTAL_POPULACAO_ANALITICA_ESPERADO,
        "555_incompleto": TOTAL_555_SEM_RESULTADO_ESPERADO,
        "888_completo": TOTAL_888_COM_RESULTADO_ESPERADO,
    }

    if contagens != esperado:
        raise RuntimeError(
            "Diagnóstico independente da população divergiu.\n"
            f"Esperado={esperado}\n"
            f"Atual={contagens}"
        )

    selecionados = dados.loc[
        tp_pres.eq(555)
        & completos
    ].copy()

    referencia = pd.DataFrame(
        index=selecionados.index
    )

    referencia[
        "ANO"
    ] = inteiro(
        selecionados[
            MAPA["NU_ANO"]
        ],
        "NU_ANO",
    )

    referencia[
        "CO_GRUPO"
    ] = inteiro(
        selecionados[
            MAPA["CO_GRUPO"]
        ],
        "CO_GRUPO",
    )

    referencia[
        "AREA_PROVA"
    ] = referencia[
        "CO_GRUPO"
    ].map(
        AREAS
    ).astype(
        "string"
    )

    referencia[
        "CO_MUNICIPIO_PROVA"
    ] = inteiro(
        selecionados[
            MAPA["CO_MUNICIPIO_PROVA"]
        ],
        "CO_MUNICIPIO_PROVA",
    )

    referencia[
        "UF_PROVA"
    ] = (
        texto_limpo(
            selecionados[
                MAPA["SG_UF_MUNICIPIO_PROVA"]
            ]
        )
        .str.upper()
    )

    for campo in [
        "TP_INSCRICAO_PND",
        "IN_REAPLICACAO",
        "CO_CADERNO",
        "TP_PRES",
        "TP_SIT_DISC",
    ]:
        referencia[
            campo
        ] = inteiro(
            selecionados[
                MAPA[campo]
            ],
            campo,
        )

    for campo in [
        "PROFICIENCIA",
        "NT_OBJ",
        "NT_DIS",
        "NT_GER",
    ]:
        referencia[
            campo
        ] = numerico(
            selecionados[
                MAPA[campo]
            ]
        ).astype(
            "Float64"
        )

    referencia[
        "QT_ACERTOS"
    ] = inteiro(
        selecionados[
            MAPA["QT_ACERTOS"]
        ],
        "QT_ACERTOS",
    )

    referencia[
        "ARQUIVO_ORIGEM"
    ] = texto_limpo(
        selecionados[
            "_arquivo_origem"
        ]
    )

    referencia[
        "LINHA_ORIGEM_BRONZE"
    ] = (
        pd.to_numeric(
            selecionados[
                "_linha_origem"
            ],
            errors="raise",
        )
        .astype(
            "int64"
        )
    )

    referencia[
        "GRANULARIDADE_ORIGEM"
    ] = texto_limpo(
        selecionados[
            "_granularidade_origem"
        ]
    )

    return (
        referencia[
            COLUNAS_SILVER
        ]
        .sort_values(
            "LINHA_ORIGEM_BRONZE"
        )
        .reset_index(
            drop=True
        )
    )


def validar_estrutura_silver(silver):
    if list(
        silver.columns
    ) != COLUNAS_SILVER:
        raise RuntimeError(
            "Esquema da Silver diferente do esperado.\n"
            f"Esperado={COLUNAS_SILVER}\n"
            f"Atual={list(silver.columns)}"
        )

    if len(silver) != TOTAL_POPULACAO_ANALITICA_ESPERADO:
        raise RuntimeError(
            f"Linhas Silver={len(silver):,}; "
            f"esperado={TOTAL_POPULACAO_ANALITICA_ESPERADO:,}."
        )

    if silver[
        "LINHA_ORIGEM_BRONZE"
    ].duplicated().any():
        raise RuntimeError(
            "LINHA_ORIGEM_BRONZE duplicada na Silver."
        )

    if set(
        silver[
            "ANO"
        ].dropna().astype(int)
    ) != {2025}:
        raise RuntimeError(
            "ANO diferente de 2025."
        )

    if set(
        silver[
            "UF_PROVA"
        ].dropna()
    ) != UFS:
        raise RuntimeError(
            "A Silver não contém exatamente as 27 UFs."
        )

    if not silver[
        "TP_PRES"
    ].eq(555).all():
        raise RuntimeError(
            "A Silver contém TP_PRES diferente de 555."
        )

    if silver[
        CAMPOS_RESULTADO
    ].isna().any().any():
        raise RuntimeError(
            "Há resultado ausente na população analítica."
        )

    if silver[
        "AREA_PROVA"
    ].isna().any():
        raise RuntimeError(
            "Há CO_GRUPO sem área oficial mapeada."
        )

    if set(
        silver[
            "GRANULARIDADE_ORIGEM"
        ].dropna()
    ) != {
        "REGISTRO_INDIVIDUAL",
    }:
        raise RuntimeError(
            "Granularidade de origem diferente de REGISTRO_INDIVIDUAL."
        )


def comparar(
    silver,
    referencia,
):
    silver_ord = (
        silver[
            COLUNAS_SILVER
        ]
        .sort_values(
            "LINHA_ORIGEM_BRONZE"
        )
        .reset_index(
            drop=True
        )
    )

    if not silver_ord[
        "LINHA_ORIGEM_BRONZE"
    ].equals(
        referencia[
            "LINHA_ORIGEM_BRONZE"
        ]
    ):
        raise RuntimeError(
            "As linhas de origem selecionadas na Silver não coincidem com a referência Bronze."
        )

    campos_float = [
        "PROFICIENCIA",
        "NT_OBJ",
        "NT_DIS",
        "NT_GER",
    ]

    divergencias = []

    for campo in COLUNAS_SILVER:
        if campo in campos_float:
            a = pd.to_numeric(
                silver_ord[
                    campo
                ],
                errors="coerce",
            ).to_numpy(
                dtype=float
            )

            b = pd.to_numeric(
                referencia[
                    campo
                ],
                errors="coerce",
            ).to_numpy(
                dtype=float
            )

            iguais = np.isclose(
                a,
                b,
                rtol=0.0,
                atol=1e-12,
                equal_nan=True,
            )
        else:
            a = (
                silver_ord[
                    campo
                ]
                .astype("string")
                .fillna(
                    "__AUSENTE__"
                )
            )

            b = (
                referencia[
                    campo
                ]
                .astype("string")
                .fillna(
                    "__AUSENTE__"
                )
            )

            iguais = (
                a.eq(
                    b
                )
                .to_numpy()
            )

        if not bool(
            np.all(
                iguais
            )
        ):
            indices = np.flatnonzero(
                ~iguais
            )[:10]

            for indice in indices:
                divergencias.append(
                    {
                        "campo": campo,
                        "linha_silver": int(
                            indice
                        ),
                        "linha_origem": silver_ord.iloc[
                            indice
                        ][
                            "LINHA_ORIGEM_BRONZE"
                        ],
                        "silver": silver_ord.iloc[
                            indice
                        ][
                            campo
                        ],
                        "bronze": referencia.iloc[
                            indice
                        ][
                            campo
                        ],
                    }
                )

    if divergencias:
        raise RuntimeError(
            "Foram encontradas divergências Silver ↔ Bronze:\n"
            + pd.DataFrame(
                divergencias
            )
            .head(30)
            .to_string(
                index=False
            )
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

    if resumo[
        "QT_ACERTOS"
    ][
        "negativos"
    ]:
        raise RuntimeError(
            "QT_ACERTOS possui valores negativos, incompatíveis com uma contagem."
        )

    return resumo


def main():
    print("=" * 110)
    print(
        "VALIDAÇÃO INDEPENDENTE — SILVER PND 2025"
    )
    print("=" * 110)
    print()

    if not BRONZE_FILE.exists():
        raise FileNotFoundError(
            f"Bronze ausente: {BRONZE_FILE}"
        )

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
        "2/4 Validando estrutura da Silver..."
    )

    validar_estrutura_silver(
        silver
    )

    print(
        "3/4 Reconstruindo população e valores diretamente da Bronze..."
    )

    bronze = pd.read_parquet(
        BRONZE_FILE,
        columns=COLUNAS_BRONZE,
    )

    validar_cabecalho(
        bronze
    )

    referencia = reconstruir_referencia(
        bronze
    )

    print(
        "4/4 Comparando os 759.140 registros Silver ↔ Bronze..."
    )

    comparar(
        silver,
        referencia,
    )

    print()
    print(
        f"Arquivo Silver: {SILVER_FILE}"
    )
    print(
        f"Linhas: {len(silver):,}"
    )
    print(
        "População: TP_PRES=555 + PROFICIENCIA, NT_OBJ, NT_DIS, NT_GER e QT_ACERTOS completos"
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
        "Resultados ausentes: 0"
    )
    print(
        "TP_PRES diferente de 555: 0"
    )
    print(
        f"Registros comparados diretamente com a Bronze: {len(referencia):,}"
    )
    print(
        "Rastreabilidade por linha de origem: OK"
    )
    print(
        "Mapeamento CO_GRUPO → área oficial: OK"
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
        "Domínio dos resultados: preservado conforme a Bronze; "
        "nenhum limite inferior não documentado foi imposto."
    )
    print()
    print(
        "SILVER DA PND 2025: OK"
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
