from pathlib import Path

import pandas as pd


SILVER_FILE = Path(
    "data/silver/rendimento/rendimento_2007_2023.parquet"
)

GOLD_DIR = Path(
    "data/gold/fatos"
)

OUTPUT_FILE = GOLD_DIR / "fato_rendimento.parquet"

COLUNAS = [
    "ANO",
    "UF",
    "ETAPA",
    "REDE",
    "INDICADOR",
    "VALOR",
]

TOTAL_ESPERADO = 2_754

ANOS_ESPERADOS = set(
    range(
        2007,
        2024,
    )
)

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

REDE_ESPERADA = {
    "PUBLICA",
}

INDICADORES_ESPERADOS = {
    "APROVACAO",
    "REPROVACAO",
    "ABANDONO",
}


def validar_estrutura_silver(
    silver,
):
    faltantes = sorted(
        set(
            COLUNAS
        )
        - set(
            silver.columns
        )
    )

    if faltantes:
        raise RuntimeError(
            "Colunas obrigatórias ausentes na Silver: "
            f"{faltantes}"
        )


def normalizar_texto(
    serie,
):
    return (
        serie
        .astype("string")
        .str.strip()
    )


def construir_fato(
    silver,
):
    fato = silver[
        COLUNAS
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

    for coluna in [
        "UF",
        "ETAPA",
        "REDE",
        "INDICADOR",
    ]:
        fato[
            coluna
        ] = normalizar_texto(
            fato[
                coluna
            ]
        )

    fato[
        "VALOR"
    ] = pd.to_numeric(
        fato[
            "VALOR"
        ],
        errors="coerce",
    ).astype(
        "Float64"
    )

    return (
        fato
        .sort_values(
            [
                "ANO",
                "UF",
                "ETAPA",
                "INDICADOR",
            ]
        )
        .reset_index(
            drop=True
        )
    )


def validar_fato(
    fato,
):
    if len(
        fato
    ) != TOTAL_ESPERADO:
        raise RuntimeError(
            f"FATO_RENDIMENTO com {len(fato):,} linhas; "
            f"esperado={TOTAL_ESPERADO:,}."
        )

    duplicadas = fato.duplicated(
        subset=[
            "ANO",
            "UF",
            "ETAPA",
            "REDE",
            "INDICADOR",
        ],
        keep=False,
    )

    if duplicadas.any():
        exemplos = (
            fato.loc[
                duplicadas
            ]
            .head(20)
            .to_dict(
                orient="records"
            )
        )

        raise RuntimeError(
            "O grão da FATO_RENDIMENTO não é único. "
            f"Exemplos={exemplos}"
        )

    anos = set(
        fato[
            "ANO"
        ].astype(
            int
        )
    )

    if anos != ANOS_ESPERADOS:
        raise RuntimeError(
            "Domínio de anos inesperado.\n"
            f"Faltantes={sorted(ANOS_ESPERADOS - anos)}\n"
            f"Extras={sorted(anos - ANOS_ESPERADOS)}"
        )

    ufs = set(
        fato[
            "UF"
        ].dropna()
    )

    if ufs != UFS_ESPERADAS:
        raise RuntimeError(
            "Domínio de UFs inesperado.\n"
            f"Faltantes={sorted(UFS_ESPERADAS - ufs)}\n"
            f"Extras={sorted(ufs - UFS_ESPERADAS)}"
        )

    etapas = set(
        fato[
            "ETAPA"
        ].dropna()
    )

    if etapas != ETAPAS_ESPERADAS:
        raise RuntimeError(
            "Domínio de etapas inesperado: "
            f"{sorted(etapas)}"
        )

    redes = set(
        fato[
            "REDE"
        ].dropna()
    )

    if redes != REDE_ESPERADA:
        raise RuntimeError(
            "Domínio de rede inesperado: "
            f"{sorted(redes)}"
        )

    indicadores = set(
        fato[
            "INDICADOR"
        ].dropna()
    )

    if indicadores != INDICADORES_ESPERADOS:
        raise RuntimeError(
            "Domínio de indicadores inesperado.\n"
            f"Faltantes={sorted(INDICADORES_ESPERADOS - indicadores)}\n"
            f"Extras={sorted(indicadores - INDICADORES_ESPERADOS)}"
        )

    if fato[
        "VALOR"
    ].isna().any():
        total = int(
            fato[
                "VALOR"
            ].isna().sum()
        )

        raise RuntimeError(
            f"FATO_RENDIMENTO contém {total} valores ausentes."
        )

    fora_dominio = (
        (
            fato[
                "VALOR"
            ] < 0
        )
        | (
            fato[
                "VALOR"
            ] > 100
        )
    )

    if fora_dominio.any():
        exemplos = (
            fato.loc[
                fora_dominio,
                [
                    "ANO",
                    "UF",
                    "ETAPA",
                    "INDICADOR",
                    "VALOR",
                ],
            ]
            .head(20)
            .to_dict(
                orient="records"
            )
        )

        raise RuntimeError(
            "FATO_RENDIMENTO contém taxas fora do domínio 0–100. "
            f"Exemplos={exemplos}"
        )


def main():
    print("=" * 110)
    print(
        "TRANSFORMAÇÃO GOLD — FATO_RENDIMENTO"
    )
    print("=" * 110)
    print()

    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Silver ausente: {SILVER_FILE}"
        )

    print(
        "1/4 Lendo Silver de Rendimento Escolar..."
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
        "3/4 Construindo fato sem recalcular as taxas..."
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

    print()
    print(
        f"Arquivo Gold: {OUTPUT_FILE}"
    )
    print(
        f"Linhas: {len(fato):,}"
    )
    print(
        f"Anos: {fato['ANO'].nunique()}"
    )
    print(
        f"UFs: {fato['UF'].nunique()}"
    )
    print(
        f"Etapas: {fato['ETAPA'].nunique()}"
    )
    print(
        f"Indicadores: {fato['INDICADOR'].nunique()}"
    )
    print(
        f"Rede: {', '.join(sorted(fato['REDE'].dropna().unique()))}"
    )
    print(
        f"Valores ausentes: {int(fato['VALOR'].isna().sum())}"
    )
    print()
    print(
        "FATO_RENDIMENTO GOLD GERADA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
