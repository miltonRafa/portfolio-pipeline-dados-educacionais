from pathlib import Path

import pandas as pd


SILVER_FILE = Path(
    "data/silver/saeb/saeb_2007_2023.parquet"
)

GOLD_DIR = Path(
    "data/gold/fatos"
)

OUTPUT_FILE = GOLD_DIR / "fato_saeb.parquet"

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

DISCIPLINAS_ESPERADAS = {
    "LP",
    "MT",
}


def normalizar_texto(
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
        "DISCIPLINA",
    ]:
        fato[
            coluna
        ] = normalizar_texto(
            fato[
                coluna
            ]
        )

    fato[
        "PROFICIENCIA"
    ] = pd.to_numeric(
        fato[
            "PROFICIENCIA"
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
                "DISCIPLINA",
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
            f"FATO_SAEB com {len(fato):,} linhas; "
            f"esperado={TOTAL_ESPERADO:,}."
        )

    duplicadas = fato.duplicated(
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
            "O grão da FATO_SAEB não é único. "
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

    disciplinas = set(
        fato[
            "DISCIPLINA"
        ].dropna()
    )

    if disciplinas != DISCIPLINAS_ESPERADAS:
        raise RuntimeError(
            "Domínio de disciplinas inesperado.\n"
            f"Faltantes={sorted(DISCIPLINAS_ESPERADAS - disciplinas)}\n"
            f"Extras={sorted(disciplinas - DISCIPLINAS_ESPERADAS)}"
        )

    if fato[
        "PROFICIENCIA"
    ].isna().any():
        total = int(
            fato[
                "PROFICIENCIA"
            ].isna().sum()
        )

        raise RuntimeError(
            f"FATO_SAEB contém {total} proficiências ausentes."
        )

    fora_dominio = (
        (
            fato[
                "PROFICIENCIA"
            ] < 0
        )
        | (
            fato[
                "PROFICIENCIA"
            ] > 500
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
                    "DISCIPLINA",
                    "PROFICIENCIA",
                ],
            ]
            .head(20)
            .to_dict(
                orient="records"
            )
        )

        raise RuntimeError(
            "FATO_SAEB contém proficiências fora do domínio 0–500. "
            f"Exemplos={exemplos}"
        )


def main():
    print("=" * 110)
    print(
        "TRANSFORMAÇÃO GOLD — FATO_SAEB"
    )
    print("=" * 110)
    print()

    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Silver ausente: {SILVER_FILE}"
        )

    print(
        "1/4 Lendo Silver do SAEB..."
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
        "3/4 Construindo fato sem recalcular proficiências..."
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
        f"Disciplinas: {fato['DISCIPLINA'].nunique()}"
    )
    print(
        f"Rede: {', '.join(sorted(fato['REDE'].dropna().unique()))}"
    )
    print(
        f"Valores ausentes: {int(fato['PROFICIENCIA'].isna().sum())}"
    )
    print()
    print(
        "FATO_SAEB GOLD GERADA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
