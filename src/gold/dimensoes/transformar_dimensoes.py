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

GOLD_DIR = Path(
    "data/gold/dimensoes"
)

OUTPUTS = {
    "dim_uf": GOLD_DIR / "dim_uf.parquet",
    "dim_tempo": GOLD_DIR / "dim_tempo.parquet",
    "dim_etapa": GOLD_DIR / "dim_etapa.parquet",
    "dim_area_pnd": GOLD_DIR / "dim_area_pnd.parquet",
    "dim_municipio": GOLD_DIR / "dim_municipio.parquet",
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
    ausentes = [
        str(caminho)
        for caminho in SILVER_FILES.values()
        if not caminho.exists()
    ]

    if ausentes:
        raise FileNotFoundError(
            "Arquivos Silver ausentes:\n"
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


def ler_colunas(
    chave,
    colunas,
):
    caminho = SILVER_FILES[
        chave
    ]

    df = pd.read_parquet(
        caminho,
        columns=colunas,
    )

    faltantes = sorted(
        set(
            colunas
        )
        - set(
            df.columns
        )
    )

    if faltantes:
        raise RuntimeError(
            f"{chave}: colunas ausentes na Silver: {faltantes}"
        )

    return df


def construir_dim_uf():
    quadros = []

    for chave in [
        "rendimento",
        "tdi",
        "ideb",
        "saeb",
    ]:
        df = ler_colunas(
            chave,
            [
                "UF",
            ],
        )

        quadros.append(
            texto_limpo(
                df[
                    "UF"
                ]
            )
            .rename(
                "UF"
            )
            .to_frame()
        )

    pnd = ler_colunas(
        "pnd",
        [
            "UF_PROVA",
        ],
    )

    quadros.append(
        texto_limpo(
            pnd[
                "UF_PROVA"
            ]
        )
        .rename(
            "UF"
        )
        .to_frame()
    )

    dim = (
        pd.concat(
            quadros,
            ignore_index=True,
        )
        .dropna()
        .drop_duplicates()
        .sort_values(
            "UF"
        )
        .reset_index(
            drop=True
        )
    )

    ufs = set(
        dim[
            "UF"
        ]
    )

    if ufs != UFS_ESPERADAS:
        raise RuntimeError(
            "DIM_UF diferente das 27 UFs esperadas.\n"
            f"Faltantes={sorted(UFS_ESPERADAS - ufs)}\n"
            f"Extras={sorted(ufs - UFS_ESPERADAS)}"
        )

    return dim


def construir_dim_tempo():
    quadros = []

    for chave in [
        "rendimento",
        "tdi",
        "ideb",
        "saeb",
        "pnd",
    ]:
        df = ler_colunas(
            chave,
            [
                "ANO",
            ],
        )

        anos = pd.to_numeric(
            df[
                "ANO"
            ],
            errors="raise",
        ).astype(
            "int64"
        )

        quadros.append(
            anos.rename(
                "ANO"
            ).to_frame()
        )

    dim = (
        pd.concat(
            quadros,
            ignore_index=True,
        )
        .drop_duplicates()
        .sort_values(
            "ANO"
        )
        .reset_index(
            drop=True
        )
    )

    anos = set(
        dim[
            "ANO"
        ].astype(
            int
        )
    )

    if anos != ANOS_ESPERADOS:
        raise RuntimeError(
            "DIM_TEMPO diferente do domínio esperado.\n"
            f"Faltantes={sorted(ANOS_ESPERADOS - anos)}\n"
            f"Extras={sorted(anos - ANOS_ESPERADOS)}"
        )

    return dim


def construir_dim_etapa():
    quadros = []

    for chave in [
        "rendimento",
        "tdi",
        "ideb",
        "saeb",
    ]:
        df = ler_colunas(
            chave,
            [
                "ETAPA",
            ],
        )

        quadros.append(
            texto_limpo(
                df[
                    "ETAPA"
                ]
            )
            .rename(
                "ETAPA"
            )
            .to_frame()
        )

    valores = (
        pd.concat(
            quadros,
            ignore_index=True,
        )
        .dropna()
        .drop_duplicates()
    )

    etapas = set(
        valores[
            "ETAPA"
        ]
    )

    if etapas != ETAPAS_ESPERADAS:
        raise RuntimeError(
            "DIM_ETAPA diferente das duas etapas esperadas.\n"
            f"Faltantes={sorted(ETAPAS_ESPERADAS - etapas)}\n"
            f"Extras={sorted(etapas - ETAPAS_ESPERADAS)}"
        )

    ordem = {
        "ANOS_INICIAIS": 1,
        "ANOS_FINAIS": 2,
    }

    dim = pd.DataFrame(
        {
            "ETAPA": [
                "ANOS_INICIAIS",
                "ANOS_FINAIS",
            ],
            "ORDEM_ETAPA": [
                1,
                2,
            ],
        }
    )

    if not dim[
        "ORDEM_ETAPA"
    ].equals(
        dim[
            "ETAPA"
        ].map(
            ordem
        )
    ):
        raise RuntimeError(
            "Ordenação da DIM_ETAPA inconsistente."
        )

    return dim


def construir_dim_area_pnd():
    pnd = ler_colunas(
        "pnd",
        [
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

    pares = (
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

    contagem_por_codigo = (
        pares
        .groupby(
            "CO_GRUPO",
            dropna=False,
        )[
            "AREA_PROVA"
        ]
        .nunique(
            dropna=False
        )
    )

    ambiguos = contagem_por_codigo[
        contagem_por_codigo
        != 1
    ]

    if not ambiguos.empty:
        raise RuntimeError(
            "CO_GRUPO com mais de um rótulo AREA_PROVA:\n"
            + ambiguos.to_string()
        )

    if len(
        pares
    ) != AREAS_PND_ESPERADAS:
        raise RuntimeError(
            f"DIM_AREA_PND com {len(pares)} linhas; "
            f"esperado={AREAS_PND_ESPERADAS}."
        )

    return pares


def construir_dim_municipio():
    pnd = ler_colunas(
        "pnd",
        [
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

    pares = (
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

    contagem_uf = (
        pares
        .groupby(
            "CO_MUNICIPIO",
            dropna=False,
        )[
            "UF"
        ]
        .nunique(
            dropna=False
        )
    )

    ambiguos = contagem_uf[
        contagem_uf
        != 1
    ]

    if not ambiguos.empty:
        raise RuntimeError(
            "Código de município associado a mais de uma UF:\n"
            + ambiguos.to_string()
        )

    if len(
        pares
    ) != MUNICIPIOS_PND_ESPERADOS:
        raise RuntimeError(
            f"DIM_MUNICIPIO com {len(pares)} linhas; "
            f"esperado={MUNICIPIOS_PND_ESPERADOS}."
        )

    ufs = set(
        pares[
            "UF"
        ]
    )

    if not ufs.issubset(
        UFS_ESPERADAS
    ):
        raise RuntimeError(
            "DIM_MUNICIPIO contém UF fora do domínio esperado: "
            f"{sorted(ufs - UFS_ESPERADAS)}"
        )

    return pares


def gravar(
    nome,
    df,
):
    caminho = OUTPUTS[
        nome
    ]

    df.to_parquet(
        caminho,
        index=False,
        engine="pyarrow",
        compression="snappy",
    )

    releitura = pd.read_parquet(
        caminho
    )

    if len(
        releitura
    ) != len(
        df
    ):
        raise RuntimeError(
            f"{nome}: quantidade de linhas mudou após gravação."
        )


def main():
    print("=" * 110)
    print(
        "TRANSFORMAÇÃO GOLD — DIMENSÕES"
    )
    print("=" * 110)
    print()

    verificar_arquivos()

    GOLD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "1/5 Construindo DIM_UF..."
    )
    dim_uf = construir_dim_uf()
    gravar(
        "dim_uf",
        dim_uf,
    )

    print(
        "2/5 Construindo DIM_TEMPO..."
    )
    dim_tempo = construir_dim_tempo()
    gravar(
        "dim_tempo",
        dim_tempo,
    )

    print(
        "3/5 Construindo DIM_ETAPA..."
    )
    dim_etapa = construir_dim_etapa()
    gravar(
        "dim_etapa",
        dim_etapa,
    )

    print(
        "4/5 Construindo DIM_AREA_PND..."
    )
    dim_area = construir_dim_area_pnd()
    gravar(
        "dim_area_pnd",
        dim_area,
    )

    print(
        "5/5 Construindo DIM_MUNICIPIO..."
    )
    dim_municipio = construir_dim_municipio()
    gravar(
        "dim_municipio",
        dim_municipio,
    )

    print()
    print(
        f"DIM_UF: {len(dim_uf)} linhas"
    )
    print(
        f"DIM_TEMPO: {len(dim_tempo)} linhas"
    )
    print(
        f"DIM_ETAPA: {len(dim_etapa)} linhas"
    )
    print(
        f"DIM_AREA_PND: {len(dim_area)} linhas"
    )
    print(
        f"DIM_MUNICIPIO: {len(dim_municipio)} linhas"
    )
    print()
    print(
        "DIMENSÕES GOLD GERADAS COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
