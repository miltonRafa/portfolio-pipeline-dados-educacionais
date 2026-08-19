from pathlib import Path

import numpy as np
import pandas as pd


SILVER_FILE = Path(
    "data/silver/pnd/pnd_2025.parquet"
)

GOLD_FILE = Path(
    "data/gold/fatos/fato_pnd.parquet"
)

DIM_FILES = {
    "uf": Path(
        "data/gold/dimensoes/dim_uf.parquet"
    ),
    "tempo": Path(
        "data/gold/dimensoes/dim_tempo.parquet"
    ),
    "area": Path(
        "data/gold/dimensoes/dim_area_pnd.parquet"
    ),
    "municipio": Path(
        "data/gold/dimensoes/dim_municipio.parquet"
    ),
}

COLUNAS_SILVER = [
    "ANO",
    "UF_PROVA",
    "CO_MUNICIPIO_PROVA",
    "CO_GRUPO",
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
]

COLUNAS_GOLD = [
    *COLUNAS_SILVER,
    "PADRAO_DESEMPENHO",
]

TOTAL_ESPERADO = 759_140

COLUNAS_CHAVE_COMPARACAO = [
    "ANO",
    "UF_PROVA",
    "CO_MUNICIPIO_PROVA",
    "CO_GRUPO",
]

COLUNAS_RESULTADO = [
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
]

CORTE_BASICO = 50.0
CORTE_ADEQUADO = 70.0

PADROES_ESPERADOS = {
    "NAO_PROFICIENTE",
    "PADRAO_1",
    "PADRAO_2",
}


def texto_limpo(
    serie,
):
    return (
        serie
        .astype("string")
        .str.strip()
    )


def classificar_padrao_desempenho(
    nt_obj,
):
    return pd.Series(
        np.select(
            [
                nt_obj < CORTE_BASICO,
                nt_obj < CORTE_ADEQUADO,
            ],
            [
                "NAO_PROFICIENTE",
                "PADRAO_1",
            ],
            default="PADRAO_2",
        ),
        index=nt_obj.index,
        dtype="string",
    )


def preparar_base(
    df,
):
    trabalho = df[
        COLUNAS_SILVER
    ].copy()

    trabalho[
        "ANO"
    ] = pd.to_numeric(
        trabalho[
            "ANO"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    trabalho[
        "UF_PROVA"
    ] = texto_limpo(
        trabalho[
            "UF_PROVA"
        ]
    )

    trabalho[
        "CO_MUNICIPIO_PROVA"
    ] = pd.to_numeric(
        trabalho[
            "CO_MUNICIPIO_PROVA"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    trabalho[
        "CO_GRUPO"
    ] = pd.to_numeric(
        trabalho[
            "CO_GRUPO"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    for coluna in [
        "PROFICIENCIA",
        "NT_OBJ",
        "NT_DIS",
        "NT_GER",
    ]:
        trabalho[
            coluna
        ] = pd.to_numeric(
            trabalho[
                coluna
            ],
            errors="coerce",
        ).astype(
            "Float64"
        )

    trabalho[
        "QT_ACERTOS"
    ] = pd.to_numeric(
        trabalho[
            "QT_ACERTOS"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    return trabalho.reset_index(
        drop=True
    )


def validar_estrutura_gold(
    gold,
):
    if list(
        gold.columns
    ) != COLUNAS_GOLD:
        raise RuntimeError(
            "Esquema da FATO_PND diferente do esperado.\n"
            f"Esperado={COLUNAS_GOLD}\n"
            f"Atual={list(gold.columns)}"
        )

    if len(
        gold
    ) != TOTAL_ESPERADO:
        raise RuntimeError(
            f"Linhas Gold={len(gold):,}; "
            f"esperado={TOTAL_ESPERADO:,}."
        )

    if set(
        pd.to_numeric(
            gold[
                "ANO"
            ],
            errors="raise",
        ).astype(
            int
        )
    ) != {
        2025,
    }:
        raise RuntimeError(
            "FATO_PND deveria conter somente 2025."
        )

    ausencias = {
        coluna: int(
            gold[
                coluna
            ].isna().sum()
        )
        for coluna in COLUNAS_GOLD
        if gold[
            coluna
        ].isna().any()
    }

    if ausencias:
        raise RuntimeError(
            f"FATO_PND contém ausências: {ausencias}"
        )

    nt_obj = pd.to_numeric(
        gold[
            "NT_OBJ"
        ],
        errors="raise",
    )

    fora_nt_obj = (
        (
            nt_obj < 0
        )
        | (
            nt_obj > 100
        )
    )

    if fora_nt_obj.any():
        raise RuntimeError(
            "FATO_PND possui NT_OBJ fora da escala oficial 0–100."
        )

    if (
        pd.to_numeric(
            gold[
                "QT_ACERTOS"
            ],
            errors="raise",
        ) < 0
    ).any():
        raise RuntimeError(
            "FATO_PND possui QT_ACERTOS negativo."
        )

    padroes = set(
        texto_limpo(
            gold[
                "PADRAO_DESEMPENHO"
            ]
        )
    )

    if padroes != PADROES_ESPERADOS:
        raise RuntimeError(
            "Domínio de PADRAO_DESEMPENHO inesperado.\n"
            f"Esperado={sorted(PADROES_ESPERADOS)}\n"
            f"Atual={sorted(padroes)}"
        )


def comparar_com_silver(
    gold,
    silver,
):
    gold_preparada = preparar_base(
        gold
    )

    silver_preparada = preparar_base(
        silver
    )

    if len(
        gold_preparada
    ) != len(
        silver_preparada
    ):
        raise RuntimeError(
            "Quantidade de registros Gold e Silver é diferente."
        )

    for coluna in COLUNAS_CHAVE_COMPARACAO:
        esquerda = (
            gold_preparada[
                coluna
            ]
            .astype("string")
            .fillna(
                "__AUSENTE__"
            )
        )

        direita = (
            silver_preparada[
                coluna
            ]
            .astype("string")
            .fillna(
                "__AUSENTE__"
            )
        )

        if not esquerda.equals(
            direita
        ):
            raise RuntimeError(
                f"Divergência Gold ↔ Silver na coluna {coluna}."
            )

    for coluna in COLUNAS_RESULTADO:
        esquerda = pd.to_numeric(
            gold_preparada[
                coluna
            ],
            errors="coerce",
        ).to_numpy(
            dtype=float
        )

        direita = pd.to_numeric(
            silver_preparada[
                coluna
            ],
            errors="coerce",
        ).to_numpy(
            dtype=float
        )

        iguais = np.isclose(
            esquerda,
            direita,
            rtol=0.0,
            atol=1e-12,
            equal_nan=True,
        )

        if not bool(
            np.all(
                iguais
            )
        ):
            indices = np.flatnonzero(
                ~iguais
            )[:20]

            exemplos = []

            for i in indices:
                exemplos.append(
                    {
                        "linha_gold": int(
                            i
                        ),
                        "campo": coluna,
                        "gold": gold_preparada.iloc[
                            i
                        ][
                            coluna
                        ],
                        "silver": silver_preparada.iloc[
                            i
                        ][
                            coluna
                        ],
                    }
                )

            raise RuntimeError(
                f"Divergência Gold ↔ Silver em {coluna}: {exemplos}"
            )


def validar_padrao_oficial(
    gold,
):
    nt_obj = pd.to_numeric(
        gold[
            "NT_OBJ"
        ],
        errors="raise",
    )

    esperado = classificar_padrao_desempenho(
        nt_obj
    )

    atual = texto_limpo(
        gold[
            "PADRAO_DESEMPENHO"
        ]
    )

    if not atual.equals(
        esperado
    ):
        divergencias = (
            gold.loc[
                atual.ne(
                    esperado
                ),
                [
                    "CO_GRUPO",
                    "NT_OBJ",
                    "PADRAO_DESEMPENHO",
                ],
            ]
            .head(20)
        )

        raise RuntimeError(
            "PADRAO_DESEMPENHO diverge dos cortes oficiais "
            "aplicados a NT_OBJ.\n"
            + divergencias.to_string(
                index=False
            )
        )


def validar_integridade_dimensional(
    gold,
):
    dim_uf = pd.read_parquet(
        DIM_FILES[
            "uf"
        ]
    )

    dim_tempo = pd.read_parquet(
        DIM_FILES[
            "tempo"
        ]
    )

    dim_area = pd.read_parquet(
        DIM_FILES[
            "area"
        ]
    )

    dim_municipio = pd.read_parquet(
        DIM_FILES[
            "municipio"
        ]
    )

    chaves_uf = set(
        texto_limpo(
            dim_uf[
                "UF"
            ]
        )
    )

    chaves_ano = set(
        pd.to_numeric(
            dim_tempo[
                "ANO"
            ],
            errors="raise",
        ).astype(
            int
        )
    )

    chaves_area = set(
        pd.to_numeric(
            dim_area[
                "CO_GRUPO"
            ],
            errors="raise",
        ).astype(
            int
        )
    )

    chaves_municipio = set(
        pd.to_numeric(
            dim_municipio[
                "CO_MUNICIPIO"
            ],
            errors="raise",
        ).astype(
            int
        )
    )

    orfas_uf = set(
        texto_limpo(
            gold[
                "UF_PROVA"
            ]
        )
    ) - chaves_uf

    orfas_ano = set(
        pd.to_numeric(
            gold[
                "ANO"
            ],
            errors="raise",
        ).astype(
            int
        )
    ) - chaves_ano

    orfas_area = set(
        pd.to_numeric(
            gold[
                "CO_GRUPO"
            ],
            errors="raise",
        ).astype(
            int
        )
    ) - chaves_area

    orfas_municipio = set(
        pd.to_numeric(
            gold[
                "CO_MUNICIPIO_PROVA"
            ],
            errors="raise",
        ).astype(
            int
        )
    ) - chaves_municipio

    if orfas_uf:
        raise RuntimeError(
            f"UFs órfãs na FATO_PND: {sorted(orfas_uf)}"
        )

    if orfas_ano:
        raise RuntimeError(
            f"Anos órfãos na FATO_PND: {sorted(orfas_ano)}"
        )

    if orfas_area:
        raise RuntimeError(
            f"Áreas órfãs na FATO_PND: {sorted(orfas_area)}"
        )

    if orfas_municipio:
        raise RuntimeError(
            f"Municípios órfãos na FATO_PND: {sorted(orfas_municipio)}"
        )

    municipio_uf = (
        dim_municipio[
            [
                "CO_MUNICIPIO",
                "UF",
            ]
        ]
        .copy()
    )

    municipio_uf[
        "CO_MUNICIPIO"
    ] = pd.to_numeric(
        municipio_uf[
            "CO_MUNICIPIO"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    municipio_uf[
        "UF"
    ] = texto_limpo(
        municipio_uf[
            "UF"
        ]
    )

    pares_fato = (
        gold[
            [
                "CO_MUNICIPIO_PROVA",
                "UF_PROVA",
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    pares_fato[
        "CO_MUNICIPIO_PROVA"
    ] = pd.to_numeric(
        pares_fato[
            "CO_MUNICIPIO_PROVA"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    pares_fato[
        "UF_PROVA"
    ] = texto_limpo(
        pares_fato[
            "UF_PROVA"
        ]
    )

    teste = pares_fato.merge(
        municipio_uf,
        left_on="CO_MUNICIPIO_PROVA",
        right_on="CO_MUNICIPIO",
        how="left",
        validate="many_to_one",
    )

    divergentes = teste.loc[
        teste[
            "UF_PROVA"
        ]
        != teste[
            "UF"
        ]
    ]

    if not divergentes.empty:
        raise RuntimeError(
            "Há município cuja UF na fato difere da DIM_MUNICIPIO.\n"
            + divergentes.head(20).to_string(
                index=False
            )
        )


def diagnosticar_numericos(
    gold,
):
    resumo = {}

    for coluna in COLUNAS_RESULTADO:
        serie = pd.to_numeric(
            gold[
                coluna
            ],
            errors="coerce",
        )

        resumo[
            coluna
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
        "VALIDAÇÃO INDEPENDENTE — FATO_PND GOLD"
    )
    print("=" * 110)
    print()

    arquivos = [
        SILVER_FILE,
        GOLD_FILE,
        *DIM_FILES.values(),
    ]

    ausentes = [
        str(
            caminho
        )
        for caminho in arquivos
        if not caminho.exists()
    ]

    if ausentes:
        raise FileNotFoundError(
            "Arquivos ausentes:\n"
            + "\n".join(
                ausentes
            )
        )

    print(
        "1/5 Lendo e validando a Gold..."
    )

    gold = pd.read_parquet(
        GOLD_FILE
    )

    validar_estrutura_gold(
        gold
    )

    print(
        "2/5 Lendo referência diretamente da Silver..."
    )

    silver = pd.read_parquet(
        SILVER_FILE,
        columns=COLUNAS_SILVER,
    )

    print(
        "3/5 Comparando os 759.140 registros Gold ↔ Silver..."
    )

    comparar_com_silver(
        gold,
        silver,
    )

    print(
        "4/5 Validando padrão oficial de desempenho..."
    )

    validar_padrao_oficial(
        gold
    )

    print(
        "5/5 Validando integridade referencial com as dimensões..."
    )

    validar_integridade_dimensional(
        gold
    )

    resumo = diagnosticar_numericos(
        gold
    )

    contagens = (
        gold[
            "PADRAO_DESEMPENHO"
        ]
        .value_counts()
        .to_dict()
    )

    proficientes = int(
        gold[
            "PADRAO_DESEMPENHO"
        ].isin(
            [
                "PADRAO_1",
                "PADRAO_2",
            ]
        ).sum()
    )

    percentual_proficientes = (
        proficientes
        / len(
            gold
        )
        * 100
    )

    print()
    print(
        f"Arquivo Gold: {GOLD_FILE}"
    )
    print(
        f"Linhas: {len(gold):,}"
    )
    print(
        "Grão preservado: um registro individual válido da prova"
    )
    print(
        f"UFs de prova: {gold['UF_PROVA'].nunique()}"
    )
    print(
        f"Áreas: {gold['CO_GRUPO'].nunique()}"
    )
    print(
        f"Municípios de prova: {gold['CO_MUNICIPIO_PROVA'].nunique():,}"
    )
    print(
        f"Registros comparados diretamente com a Silver: {len(silver):,}"
    )
    print(
        "Resultados Gold = Silver: OK"
    )
    print()
    print(
        "PADRÃO OFICIAL DE DESEMPENHO — VALIDADO"
    )
    print(
        f"Não proficiente (NT_OBJ < 50): "
        f"{contagens.get('NAO_PROFICIENTE', 0):,}"
    )
    print(
        f"Padrão 1 (50 <= NT_OBJ < 70): "
        f"{contagens.get('PADRAO_1', 0):,}"
    )
    print(
        f"Padrão 2 (NT_OBJ >= 70): "
        f"{contagens.get('PADRAO_2', 0):,}"
    )
    print(
        f"Proficientes (Padrão 1 + Padrão 2): "
        f"{proficientes:,} ({percentual_proficientes:.2f}%)"
    )
    print(
        "NT_OBJ na escala oficial 0–100: OK"
    )
    print()
    print(
        "Chaves órfãs em DIM_UF: 0"
    )
    print(
        "Chaves órfãs em DIM_TEMPO: 0"
    )
    print(
        "Chaves órfãs em DIM_AREA_PND: 0"
    )
    print(
        "Chaves órfãs em DIM_MUNICIPIO: 0"
    )
    print(
        "Coerência Município → UF_PROVA: OK"
    )
    print()
    print(
        "DIAGNÓSTICO DOS RESULTADOS NUMÉRICOS"
    )

    for coluna, valores in resumo.items():
        print(
            f"{coluna}: "
            f"mín={valores['min']:.6f} | "
            f"máx={valores['max']:.6f} | "
            f"negativos={valores['negativos']:,}"
        )

    print()
    print(
        "PROFICIENCIA negativa é preservada quando publicada pela fonte."
    )
    print(
        "A classificação oficial usa NT_OBJ; NT_GER e NT_DIS permanecem medidas descritivas."
    )
    print()
    print(
        "FATO_PND GOLD: OK"
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
