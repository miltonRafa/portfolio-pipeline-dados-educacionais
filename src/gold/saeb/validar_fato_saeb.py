from pathlib import Path

import numpy as np
import pandas as pd


SILVER_FILE = Path(
    "data/silver/saeb/saeb_2007_2023.parquet"
)

GOLD_FILE = Path(
    "data/gold/fatos/fato_saeb.parquet"
)

DIM_FILES = {
    "uf": Path(
        "data/gold/dimensoes/dim_uf.parquet"
    ),
    "tempo": Path(
        "data/gold/dimensoes/dim_tempo.parquet"
    ),
    "etapa": Path(
        "data/gold/dimensoes/dim_etapa.parquet"
    ),
}

COLUNAS = [
    "ANO",
    "UF",
    "ETAPA",
    "REDE",
    "DISCIPLINA",
    "PROFICIENCIA",
]

TOTAL_ESPERADO = 972

ANOS_ESPERADOS = {
    2007,
    2009,
    2011,
    2013,
    2015,
    2017,
    2019,
    2021,
    2023,
}

DISCIPLINAS_ESPERADAS = {
    "LP",
    "MT",
}


def texto_limpo(
    serie,
):
    return (
        serie
        .astype("string")
        .str.strip()
    )


def carregar_referencia_silver():
    silver = pd.read_parquet(
        SILVER_FILE,
        columns=COLUNAS,
    ).copy()

    silver[
        "ANO"
    ] = pd.to_numeric(
        silver[
            "ANO"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    for coluna in [
        "UF",
        "ETAPA",
        "REDE",
        "DISCIPLINA",
    ]:
        silver[
            coluna
        ] = texto_limpo(
            silver[
                coluna
            ]
        )

    silver[
        "PROFICIENCIA"
    ] = pd.to_numeric(
        silver[
            "PROFICIENCIA"
        ],
        errors="coerce",
    ).astype(
        "Float64"
    )

    return (
        silver
        .sort_values(
            [
                "ANO",
                "UF",
                "ETAPA",
                "DISCIPLINA",
            ]
        )
        .reset_index(
            drop=True
        )
    )


def validar_estrutura_gold(
    gold,
):
    if list(
        gold.columns
    ) != COLUNAS:
        raise RuntimeError(
            "Esquema da FATO_SAEB diferente do esperado.\n"
            f"Esperado={COLUNAS}\n"
            f"Atual={list(gold.columns)}"
        )

    if len(
        gold
    ) != TOTAL_ESPERADO:
        raise RuntimeError(
            f"Linhas Gold={len(gold):,}; "
            f"esperado={TOTAL_ESPERADO:,}."
        )

    duplicadas = gold.duplicated(
        subset=[
            "ANO",
            "UF",
            "ETAPA",
            "REDE",
            "DISCIPLINA",
        ],
        keep=False,
    )

    if duplicadas.any():
        raise RuntimeError(
            "O grão da FATO_SAEB possui duplicidades."
        )

    anos = set(
        pd.to_numeric(
            gold[
                "ANO"
            ],
            errors="raise",
        ).astype(
            int
        )
    )

    if anos != ANOS_ESPERADOS:
        raise RuntimeError(
            "A Gold não possui exatamente as nove edições esperadas."
        )

    disciplinas = set(
        texto_limpo(
            gold[
                "DISCIPLINA"
            ]
        )
    )

    if disciplinas != DISCIPLINAS_ESPERADAS:
        raise RuntimeError(
            f"Disciplinas inesperadas: {sorted(disciplinas)}"
        )

    if gold[
        "PROFICIENCIA"
    ].isna().any():
        raise RuntimeError(
            "A Gold contém PROFICIENCIA ausente."
        )

    fora = (
        (
            gold[
                "PROFICIENCIA"
            ] < 0
        )
        | (
            gold[
                "PROFICIENCIA"
            ] > 500
        )
    )

    if fora.any():
        raise RuntimeError(
            "A Gold contém proficiência fora do domínio 0–500."
        )


def comparar_com_silver(
    gold,
    referencia,
):
    atual = (
        gold[
            COLUNAS
        ]
        .sort_values(
            [
                "ANO",
                "UF",
                "ETAPA",
                "DISCIPLINA",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    for coluna in [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "DISCIPLINA",
    ]:
        a = (
            atual[
                coluna
            ]
            .astype("string")
            .fillna(
                "__AUSENTE__"
            )
        )

        b = (
            referencia[
                coluna
            ]
            .astype("string")
            .fillna(
                "__AUSENTE__"
            )
        )

        if not a.equals(
            b
        ):
            raise RuntimeError(
                f"Divergência Gold ↔ Silver na coluna {coluna}."
            )

    a = pd.to_numeric(
        atual[
            "PROFICIENCIA"
        ],
        errors="coerce",
    ).to_numpy(
        dtype=float
    )

    b = pd.to_numeric(
        referencia[
            "PROFICIENCIA"
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
                    "ANO": atual.iloc[
                        i
                    ][
                        "ANO"
                    ],
                    "UF": atual.iloc[
                        i
                    ][
                        "UF"
                    ],
                    "ETAPA": atual.iloc[
                        i
                    ][
                        "ETAPA"
                    ],
                    "DISCIPLINA": atual.iloc[
                        i
                    ][
                        "DISCIPLINA"
                    ],
                    "GOLD": atual.iloc[
                        i
                    ][
                        "PROFICIENCIA"
                    ],
                    "SILVER": referencia.iloc[
                        i
                    ][
                        "PROFICIENCIA"
                    ],
                }
            )

        raise RuntimeError(
            "Foram encontradas proficiências Gold diferentes da Silver: "
            f"{exemplos}"
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

    dim_etapa = pd.read_parquet(
        DIM_FILES[
            "etapa"
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

    chaves_etapa = set(
        texto_limpo(
            dim_etapa[
                "ETAPA"
            ]
        )
    )

    orfas_uf = set(
        texto_limpo(
            gold[
                "UF"
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

    orfas_etapa = set(
        texto_limpo(
            gold[
                "ETAPA"
            ]
        )
    ) - chaves_etapa

    if orfas_uf:
        raise RuntimeError(
            f"UFs órfãs na FATO_SAEB: {sorted(orfas_uf)}"
        )

    if orfas_ano:
        raise RuntimeError(
            f"Anos órfãos na FATO_SAEB: {sorted(orfas_ano)}"
        )

    if orfas_etapa:
        raise RuntimeError(
            f"Etapas órfãs na FATO_SAEB: {sorted(orfas_etapa)}"
        )


def main():
    print("=" * 110)
    print(
        "VALIDAÇÃO INDEPENDENTE — FATO_SAEB GOLD"
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
        "1/4 Lendo e validando a Gold..."
    )

    gold = pd.read_parquet(
        GOLD_FILE
    )

    validar_estrutura_gold(
        gold
    )

    print(
        "2/4 Reconstruindo referência diretamente da Silver..."
    )

    referencia = carregar_referencia_silver()

    print(
        "3/4 Comparando Gold ↔ Silver..."
    )

    comparar_com_silver(
        gold,
        referencia,
    )

    print(
        "4/4 Validando integridade referencial com as dimensões..."
    )

    validar_integridade_dimensional(
        gold
    )

    print()
    print(
        f"Arquivo Gold: {GOLD_FILE}"
    )
    print(
        f"Linhas: {len(gold):,}"
    )
    print(
        "Grão único ANO + UF + ETAPA + REDE + DISCIPLINA: OK"
    )
    print(
        f"Edições: {len(ANOS_ESPERADOS)}"
    )
    print(
        "Disciplinas: LP, MT"
    )
    print(
        f"Registros comparados diretamente com a Silver: {len(referencia):,}"
    )
    print(
        "Proficiências Gold = Silver: OK"
    )
    print(
        "Domínio da proficiência 0–500: OK"
    )
    print(
        "Chaves órfãs em DIM_UF: 0"
    )
    print(
        "Chaves órfãs em DIM_TEMPO: 0"
    )
    print(
        "Chaves órfãs em DIM_ETAPA: 0"
    )
    print()
    print(
        "FATO_SAEB GOLD: OK"
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
