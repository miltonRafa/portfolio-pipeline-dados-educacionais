from pathlib import Path

import pandas as pd

if __package__:
    from .classificacao import PADROES_ESPERADOS, classificar_nivel_desempenho
else:
    from classificacao import PADROES_ESPERADOS, classificar_nivel_desempenho


SILVER_FILE = Path(
    "data/silver/pnd/pnd_2025.parquet"
)

GOLD_DIR = Path(
    "data/gold/fatos"
)

OUTPUT_FILE = GOLD_DIR / "fato_pnd.parquet"

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

UFS_ESPERADAS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF",
    "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
    "RO", "RR", "SC", "SP", "SE", "TO",
}

AREAS_ESPERADAS = 17
MUNICIPIOS_ESPERADOS = 750

# Classificacao compartilhada por NT_GER publicada (AUD-04B).


def texto_limpo(
    serie,
):
    return (
        serie
        .astype("string")
        .str.strip()
    )


def validar_estrutura_silver(
    silver,
):
    faltantes = sorted(
        set(
            COLUNAS_SILVER
        )
        - set(
            silver.columns
        )
    )

    if faltantes:
        raise RuntimeError(
            "Colunas obrigatórias ausentes na Silver da PND: "
            f"{faltantes}"
        )



def construir_fato(
    silver,
):
    fato = silver[
        COLUNAS_SILVER
    ].copy()

    fato[
        "ANO"
    ] = pd.to_numeric(
        fato[
            "ANO"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    fato[
        "UF_PROVA"
    ] = texto_limpo(
        fato[
            "UF_PROVA"
        ]
    )

    fato[
        "CO_MUNICIPIO_PROVA"
    ] = pd.to_numeric(
        fato[
            "CO_MUNICIPIO_PROVA"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    fato[
        "CO_GRUPO"
    ] = pd.to_numeric(
        fato[
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
        fato[
            coluna
        ] = pd.to_numeric(
            fato[
                coluna
            ],
            errors="coerce",
        ).astype(
            "Float64"
        )

    fato[
        "QT_ACERTOS"
    ] = pd.to_numeric(
        fato[
            "QT_ACERTOS"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    # Nivel oficial DD pela nota geral, incluindo a componente discursiva.
    fato[
        "PADRAO_DESEMPENHO"
    ] = classificar_nivel_desempenho(
        fato[
            "NT_GER"
        ]
    )

    return fato[
        COLUNAS_GOLD
    ].reset_index(
        drop=True
    )


def validar_fato(
    fato,
):
    if len(
        fato
    ) != TOTAL_ESPERADO:
        raise RuntimeError(
            f"FATO_PND com {len(fato):,} linhas; "
            f"esperado={TOTAL_ESPERADO:,}."
        )

    if set(
        fato[
            "ANO"
        ].astype(
            int
        )
    ) != {
        2025,
    }:
        raise RuntimeError(
            "FATO_PND deveria conter apenas o ano 2025."
        )

    ufs = set(
        fato[
            "UF_PROVA"
        ].dropna()
    )

    if ufs != UFS_ESPERADAS:
        raise RuntimeError(
            "Domínio de UFs da PND inesperado.\n"
            f"Faltantes={sorted(UFS_ESPERADAS - ufs)}\n"
            f"Extras={sorted(ufs - UFS_ESPERADAS)}"
        )

    if fato[
        "CO_GRUPO"
    ].nunique() != AREAS_ESPERADAS:
        raise RuntimeError(
            f"FATO_PND possui {fato['CO_GRUPO'].nunique()} grupos; "
            f"esperado={AREAS_ESPERADAS}."
        )

    if fato[
        "CO_MUNICIPIO_PROVA"
    ].nunique() != MUNICIPIOS_ESPERADOS:
        raise RuntimeError(
            f"FATO_PND possui {fato['CO_MUNICIPIO_PROVA'].nunique()} municípios; "
            f"esperado={MUNICIPIOS_ESPERADOS}."
        )

    ausencias = {
        coluna: int(
            fato[
                coluna
            ].isna().sum()
        )
        for coluna in COLUNAS_GOLD
        if fato[
            coluna
        ].isna().any()
    }

    if ausencias:
        raise RuntimeError(
            f"FATO_PND contém ausências: {ausencias}"
        )

    # NT_OBJ possui escala oficial de divulgação 0–100.
    fora_nt_obj = (
        (
            fato[
                "NT_OBJ"
            ] < 0
        )
        | (
            fato[
                "NT_OBJ"
            ] > 100
        )
    )

    if fora_nt_obj.any():
        exemplos = (
            fato.loc[
                fora_nt_obj,
                [
                    "CO_GRUPO",
                    "NT_OBJ",
                ],
            ]
            .head(20)
            .to_dict(
                orient="records"
            )
        )

        raise RuntimeError(
            "NT_OBJ contém valores fora da escala oficial 0–100. "
            f"Exemplos={exemplos}"
        )

    if (
        fato[
            "QT_ACERTOS"
        ] < 0
    ).any():
        exemplos = (
            fato.loc[
                fato[
                    "QT_ACERTOS"
                ] < 0,
                [
                    "ANO",
                    "UF_PROVA",
                    "CO_MUNICIPIO_PROVA",
                    "CO_GRUPO",
                    "QT_ACERTOS",
                ],
            ]
            .head(20)
            .to_dict(
                orient="records"
            )
        )

        raise RuntimeError(
            "QT_ACERTOS contém valores negativos. "
            f"Exemplos={exemplos}"
        )

    padroes = set(
        fato[
            "PADRAO_DESEMPENHO"
        ].dropna()
    )

    if padroes != PADROES_ESPERADOS:
        raise RuntimeError(
            "Domínio de PADRAO_DESEMPENHO inesperado.\n"
            f"Esperado={sorted(PADROES_ESPERADOS)}\n"
            f"Atual={sorted(padroes)}"
        )

    esperado = classificar_nivel_desempenho(
        fato[
            "NT_GER"
        ]
    )

    if not fato[
        "PADRAO_DESEMPENHO"
    ].equals(
        esperado
    ):
        raise RuntimeError(
            "PADRAO_DESEMPENHO não corresponde aos cortes oficiais "
            "aplicados sobre NT_GER."
        )


def main():
    print("=" * 110)
    print(
        "TRANSFORMAÇÃO GOLD — FATO_PND"
    )
    print("=" * 110)
    print()

    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Silver ausente: {SILVER_FILE}"
        )

    print(
        "1/4 Lendo Silver da PND 2025..."
    )

    silver = pd.read_parquet(
        SILVER_FILE
    )

    print(
        "2/4 Validando estrutura de entrada..."
    )

    validar_estrutura_silver(
        silver
    )

    print(
        "3/4 Construindo fato individual e padrão oficial de desempenho..."
    )

    fato = construir_fato(
        silver
    )

    validar_fato(
        fato
    )

    print(
        "4/4 Gravando Parquet Gold..."
    )

    GOLD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fato.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow",
        compression="snappy",
    )

    releitura = pd.read_parquet(
        OUTPUT_FILE
    )

    if len(
        releitura
    ) != len(
        fato
    ):
        raise RuntimeError(
            "Quantidade de linhas mudou após gravação."
        )

    contagens = (
        fato[
            "PADRAO_DESEMPENHO"
        ]
        .value_counts()
        .to_dict()
    )

    basico_ou_adequado = int(
        fato[
            "PADRAO_DESEMPENHO"
        ].isin(
            [
                "BASICO",
                "ADEQUADO",
            ]
        ).sum()
    )

    percentual_basico_ou_adequado = (
        basico_ou_adequado
        / len(
            fato
        )
        * 100
    )

    print()
    print(
        f"Arquivo Gold: {OUTPUT_FILE}"
    )
    print(
        f"Linhas: {len(fato):,}"
    )
    print(
        f"Ano: {', '.join(map(str, sorted(fato['ANO'].unique())))}"
    )
    print(
        f"UFs de prova: {fato['UF_PROVA'].nunique()}"
    )
    print(
        f"Áreas: {fato['CO_GRUPO'].nunique()}"
    )
    print(
        f"Municípios de prova: {fato['CO_MUNICIPIO_PROVA'].nunique():,}"
    )
    print(
        "Resultados ausentes: 0"
    )
    print()
    print(
        "NÍVEL DE DESEMPENHO DOCENTE — NT_GER"
    )
    print(
        f"Abaixo do Básico (NT_GER < 50): "
        f"{contagens.get('ABAIXO_DO_BASICO', 0):,}"
    )
    print(
        f"Básico (50 <= NT_GER < 70): "
        f"{contagens.get('BASICO', 0):,}"
    )
    print(
        f"Adequado (NT_GER >= 70): "
        f"{contagens.get('ADEQUADO', 0):,}"
    )
    print(
        f"Básico ou Adequado: "
        f"{basico_ou_adequado:,} ({percentual_basico_ou_adequado:.2f}%)"
    )
    print()
    print(
        f"PROFICIENCIA: mín={fato['PROFICIENCIA'].min():.6f} | "
        f"máx={fato['PROFICIENCIA'].max():.6f}"
    )
    print(
        f"NT_OBJ: mín={fato['NT_OBJ'].min():.6f} | "
        f"máx={fato['NT_OBJ'].max():.6f}"
    )
    print(
        f"NT_DIS: mín={fato['NT_DIS'].min():.6f} | "
        f"máx={fato['NT_DIS'].max():.6f}"
    )
    print(
        f"NT_GER: mín={fato['NT_GER'].min():.6f} | "
        f"máx={fato['NT_GER'].max():.6f}"
    )
    print(
        f"QT_ACERTOS: mín={fato['QT_ACERTOS'].min()} | "
        f"máx={fato['QT_ACERTOS'].max()}"
    )
    print()
    print(
        "FATO_PND GOLD GERADA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
