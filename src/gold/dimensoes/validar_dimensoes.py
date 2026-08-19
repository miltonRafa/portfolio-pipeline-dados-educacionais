from pathlib import Path

import pandas as pd


SILVER_FILES = {
    "rendimento": Path(
        "data/silver/rendimento/rendimento_2007_2023.parquet"
    ),
    "tdi": Path(
        "data/silver/tdi/tdi_2007_2023.parquet"
    ),
    "ideb": Path(
        "data/silver/ideb/ideb_2007_2023.parquet"
    ),
    "saeb": Path(
        "data/silver/saeb/saeb_2007_2023.parquet"
    ),
    "pnd": Path(
        "data/silver/pnd/pnd_2025.parquet"
    ),
}

GOLD_FILES = {
    "dim_uf": Path(
        "data/gold/dimensoes/dim_uf.parquet"
    ),
    "dim_tempo": Path(
        "data/gold/dimensoes/dim_tempo.parquet"
    ),
    "dim_etapa": Path(
        "data/gold/dimensoes/dim_etapa.parquet"
    ),
    "dim_area_pnd": Path(
        "data/gold/dimensoes/dim_area_pnd.parquet"
    ),
    "dim_municipio": Path(
        "data/gold/dimensoes/dim_municipio.parquet"
    ),
}

UFS_ESPERADAS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF",
    "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
    "RO", "RR", "SC", "SP", "SE", "TO",
}

ETAPAS_ESPERADAS = {
    "ANOS_INICIAIS",
    "ANOS_FINAIS",
}

ANOS_ESPERADOS = set(
    range(
        2007,
        2024,
    )
) | {
    2025,
}

AREAS_PND_ESPERADAS = 17
MUNICIPIOS_PND_ESPERADOS = 750


def verificar_arquivos():
    ausentes = []

    for caminho in [
        *SILVER_FILES.values(),
        *GOLD_FILES.values(),
    ]:
        if not caminho.exists():
            ausentes.append(
                str(
                    caminho
                )
            )

    if ausentes:
        raise FileNotFoundError(
            "Arquivos ausentes:\n"
            + "\n".join(
                ausentes
            )
        )


def texto_limpo(serie):
    return (
        serie
        .astype("string")
        .str.strip()
    )


def validar_dim_uf():
    dim = pd.read_parquet(
        GOLD_FILES[
            "dim_uf"
        ]
    )

    if list(
        dim.columns
    ) != [
        "UF",
    ]:
        raise RuntimeError(
            f"DIM_UF: esquema inesperado {list(dim.columns)}"
        )

    if dim[
        "UF"
    ].duplicated().any():
        raise RuntimeError(
            "DIM_UF possui chave duplicada."
        )

    ufs = set(
        texto_limpo(
            dim[
                "UF"
            ]
        )
    )

    if ufs != UFS_ESPERADAS:
        raise RuntimeError(
            "DIM_UF diferente das 27 UFs esperadas."
        )

    origens = []

    for chave in [
        "rendimento",
        "tdi",
        "ideb",
        "saeb",
    ]:
        df = pd.read_parquet(
            SILVER_FILES[
                chave
            ],
            columns=[
                "UF",
            ],
        )

        origens.extend(
            texto_limpo(
                df[
                    "UF"
                ]
            )
            .dropna()
            .tolist()
        )

    pnd = pd.read_parquet(
        SILVER_FILES[
            "pnd"
        ],
        columns=[
            "UF_PROVA",
        ],
    )

    origens.extend(
        texto_limpo(
            pnd[
                "UF_PROVA"
            ]
        )
        .dropna()
        .tolist()
    )

    if set(
        origens
    ) != ufs:
        raise RuntimeError(
            "DIM_UF não corresponde à união das UFs das Silvers."
        )

    return len(
        dim
    )


def validar_dim_tempo():
    dim = pd.read_parquet(
        GOLD_FILES[
            "dim_tempo"
        ]
    )

    if list(
        dim.columns
    ) != [
        "ANO",
    ]:
        raise RuntimeError(
            f"DIM_TEMPO: esquema inesperado {list(dim.columns)}"
        )

    if dim[
        "ANO"
    ].duplicated().any():
        raise RuntimeError(
            "DIM_TEMPO possui chave duplicada."
        )

    anos = set(
        pd.to_numeric(
            dim[
                "ANO"
            ],
            errors="raise",
        ).astype(
            int
        )
    )

    if anos != ANOS_ESPERADOS:
        raise RuntimeError(
            "DIM_TEMPO diferente do domínio esperado."
        )

    anos_origem = set()

    for chave in SILVER_FILES:
        df = pd.read_parquet(
            SILVER_FILES[
                chave
            ],
            columns=[
                "ANO",
            ],
        )

        anos_origem.update(
            pd.to_numeric(
                df[
                    "ANO"
                ],
                errors="raise",
            )
            .astype(
                int
            )
            .tolist()
        )

    if anos_origem != anos:
        raise RuntimeError(
            "DIM_TEMPO não corresponde à união dos anos das Silvers."
        )

    return len(
        dim
    )


def validar_dim_etapa():
    dim = pd.read_parquet(
        GOLD_FILES[
            "dim_etapa"
        ]
    )

    esperadas = [
        "ETAPA",
        "ORDEM_ETAPA",
    ]

    if list(
        dim.columns
    ) != esperadas:
        raise RuntimeError(
            f"DIM_ETAPA: esquema inesperado {list(dim.columns)}"
        )

    if dim[
        "ETAPA"
    ].duplicated().any():
        raise RuntimeError(
            "DIM_ETAPA possui chave duplicada."
        )

    etapas = set(
        texto_limpo(
            dim[
                "ETAPA"
            ]
        )
    )

    if etapas != ETAPAS_ESPERADAS:
        raise RuntimeError(
            "DIM_ETAPA diferente do domínio esperado."
        )

    ordem = dict(
        zip(
            dim[
                "ETAPA"
            ],
            dim[
                "ORDEM_ETAPA"
            ],
        )
    )

    if ordem != {
        "ANOS_INICIAIS": 1,
        "ANOS_FINAIS": 2,
    }:
        raise RuntimeError(
            f"DIM_ETAPA com ordenação inesperada: {ordem}"
        )

    etapas_origem = set()

    for chave in [
        "rendimento",
        "tdi",
        "ideb",
        "saeb",
    ]:
        df = pd.read_parquet(
            SILVER_FILES[
                chave
            ],
            columns=[
                "ETAPA",
            ],
        )

        etapas_origem.update(
            texto_limpo(
                df[
                    "ETAPA"
                ]
            )
            .dropna()
            .tolist()
        )

    if etapas_origem != etapas:
        raise RuntimeError(
            "DIM_ETAPA não corresponde às etapas das Silvers."
        )

    return len(
        dim
    )


def validar_dim_area_pnd():
    dim = pd.read_parquet(
        GOLD_FILES[
            "dim_area_pnd"
        ]
    )

    esperadas = [
        "CO_GRUPO",
        "AREA_PROVA",
    ]

    if list(
        dim.columns
    ) != esperadas:
        raise RuntimeError(
            f"DIM_AREA_PND: esquema inesperado {list(dim.columns)}"
        )

    if dim[
        "CO_GRUPO"
    ].duplicated().any():
        raise RuntimeError(
            "DIM_AREA_PND possui CO_GRUPO duplicado."
        )

    if len(
        dim
    ) != AREAS_PND_ESPERADAS:
        raise RuntimeError(
            f"DIM_AREA_PND com {len(dim)} linhas; "
            f"esperado={AREAS_PND_ESPERADAS}."
        )

    pnd = pd.read_parquet(
        SILVER_FILES[
            "pnd"
        ],
        columns=[
            "CO_GRUPO",
            "AREA_PROVA",
        ],
    ).copy()

    pnd[
        "CO_GRUPO"
    ] = pd.to_numeric(
        pnd[
            "CO_GRUPO"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    pnd[
        "AREA_PROVA"
    ] = texto_limpo(
        pnd[
            "AREA_PROVA"
        ]
    )

    referencia = (
        pnd[
            [
                "CO_GRUPO",
                "AREA_PROVA",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            "CO_GRUPO"
        )
        .reset_index(
            drop=True
        )
    )

    atual = (
        dim[
            esperadas
        ]
        .sort_values(
            "CO_GRUPO"
        )
        .reset_index(
            drop=True
        )
    )

    if not atual.equals(
        referencia
    ):
        raise RuntimeError(
            "DIM_AREA_PND não reproduz exatamente os pares únicos da Silver."
        )

    return len(
        dim
    )


def validar_dim_municipio():
    dim = pd.read_parquet(
        GOLD_FILES[
            "dim_municipio"
        ]
    )

    esperadas = [
        "CO_MUNICIPIO",
        "UF",
    ]

    if list(
        dim.columns
    ) != esperadas:
        raise RuntimeError(
            f"DIM_MUNICIPIO: esquema inesperado {list(dim.columns)}"
        )

    if dim[
        "CO_MUNICIPIO"
    ].duplicated().any():
        raise RuntimeError(
            "DIM_MUNICIPIO possui código de município duplicado."
        )

    if len(
        dim
    ) != MUNICIPIOS_PND_ESPERADOS:
        raise RuntimeError(
            f"DIM_MUNICIPIO com {len(dim)} linhas; "
            f"esperado={MUNICIPIOS_PND_ESPERADOS}."
        )

    pnd = pd.read_parquet(
        SILVER_FILES[
            "pnd"
        ],
        columns=[
            "CO_MUNICIPIO_PROVA",
            "UF_PROVA",
        ],
    ).copy()

    pnd[
        "CO_MUNICIPIO"
    ] = pd.to_numeric(
        pnd[
            "CO_MUNICIPIO_PROVA"
        ],
        errors="raise",
    ).astype(
        "int64"
    )

    pnd[
        "UF"
    ] = texto_limpo(
        pnd[
            "UF_PROVA"
        ]
    )

    referencia = (
        pnd[
            [
                "CO_MUNICIPIO",
                "UF",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "UF",
                "CO_MUNICIPIO",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    atual = (
        dim[
            esperadas
        ]
        .sort_values(
            [
                "UF",
                "CO_MUNICIPIO",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    if not atual.equals(
        referencia
    ):
        raise RuntimeError(
            "DIM_MUNICIPIO não reproduz exatamente os pares município/UF da Silver PND."
        )

    if not set(
        atual[
            "UF"
        ]
    ).issubset(
        UFS_ESPERADAS
    ):
        raise RuntimeError(
            "DIM_MUNICIPIO contém UF inválida."
        )

    return len(
        dim
    )


def main():
    print("=" * 110)
    print(
        "VALIDAÇÃO INDEPENDENTE — DIMENSÕES GOLD"
    )
    print("=" * 110)
    print()

    verificar_arquivos()

    print(
        "1/5 Validando DIM_UF..."
    )
    n_uf = validar_dim_uf()

    print(
        "2/5 Validando DIM_TEMPO..."
    )
    n_tempo = validar_dim_tempo()

    print(
        "3/5 Validando DIM_ETAPA..."
    )
    n_etapa = validar_dim_etapa()

    print(
        "4/5 Validando DIM_AREA_PND..."
    )
    n_area = validar_dim_area_pnd()

    print(
        "5/5 Validando DIM_MUNICIPIO..."
    )
    n_municipio = validar_dim_municipio()

    print()
    print(
        f"DIM_UF: {n_uf} linhas | chave única: OK"
    )
    print(
        f"DIM_TEMPO: {n_tempo} linhas | chave única: OK"
    )
    print(
        f"DIM_ETAPA: {n_etapa} linhas | chave única: OK"
    )
    print(
        f"DIM_AREA_PND: {n_area} linhas | CO_GRUPO único: OK"
    )
    print(
        f"DIM_MUNICIPIO: {n_municipio} linhas | CO_MUNICIPIO único: OK"
    )
    print()
    print(
        "Reprodução das Silvers: OK"
    )
    print(
        "Domínios dimensionais: OK"
    )
    print()
    print(
        "DIMENSÕES GOLD: OK"
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
