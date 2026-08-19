from pathlib import Path

import numpy as np
import pandas as pd


DIM_DIR = Path(
    "data/gold/dimensoes"
)

FATO_DIR = Path(
    "data/gold/fatos"
)

ARQUIVOS = {
    "DIM_UF": DIM_DIR / "dim_uf.parquet",
    "DIM_TEMPO": DIM_DIR / "dim_tempo.parquet",
    "DIM_ETAPA": DIM_DIR / "dim_etapa.parquet",
    "DIM_AREA_PND": DIM_DIR / "dim_area_pnd.parquet",
    "DIM_MUNICIPIO": DIM_DIR / "dim_municipio.parquet",
    "FATO_RENDIMENTO": FATO_DIR / "fato_rendimento.parquet",
    "FATO_TDI": FATO_DIR / "fato_tdi.parquet",
    "FATO_IDEB": FATO_DIR / "fato_ideb.parquet",
    "FATO_SAEB": FATO_DIR / "fato_saeb.parquet",
    "FATO_PND": FATO_DIR / "fato_pnd.parquet",
}

COLUNAS_ESPERADAS = {
    "DIM_UF": [
        "UF",
    ],
    "DIM_TEMPO": [
        "ANO",
    ],
    "DIM_ETAPA": [
        "ETAPA",
        "ORDEM_ETAPA",
    ],
    "DIM_AREA_PND": [
        "CO_GRUPO",
        "AREA_PROVA",
    ],
    "DIM_MUNICIPIO": [
        "CO_MUNICIPIO",
        "UF",
    ],
    "FATO_RENDIMENTO": [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "INDICADOR",
        "VALOR",
    ],
    "FATO_TDI": [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "TDI",
    ],
    "FATO_IDEB": [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "IDEB",
    ],
    "FATO_SAEB": [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "DISCIPLINA",
        "PROFICIENCIA",
    ],
    "FATO_PND": [
        "ANO",
        "UF_PROVA",
        "CO_MUNICIPIO_PROVA",
        "CO_GRUPO",
        "PROFICIENCIA",
        "NT_OBJ",
        "NT_DIS",
        "NT_GER",
        "QT_ACERTOS",
        "PADRAO_DESEMPENHO",
    ],
}

LINHAS_ESPERADAS = {
    "DIM_UF": 27,
    "DIM_TEMPO": 18,
    "DIM_ETAPA": 2,
    "DIM_AREA_PND": 17,
    "DIM_MUNICIPIO": 750,
    "FATO_RENDIMENTO": 2_754,
    "FATO_TDI": 918,
    "FATO_IDEB": 486,
    "FATO_SAEB": 972,
    "FATO_PND": 759_140,
}

UFS_ESPERADAS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF",
    "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
    "RO", "RR", "SC", "SP", "SE", "TO",
}

ANOS_DIM_TEMPO_ESPERADOS = {
    *range(
        2007,
        2024,
    ),
    2025,
}

ANOS_HISTORICOS_ANUAIS = set(
    range(
        2007,
        2024,
    )
)

ANOS_BIENAIS = {
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

ETAPAS_ESPERADAS = {
    "ANOS_INICIAIS",
    "ANOS_FINAIS",
}

ORDEM_ETAPAS_ESPERADA = {
    "ANOS_INICIAIS": 1,
    "ANOS_FINAIS": 2,
}

INDICADORES_RENDIMENTO = {
    "APROVACAO",
    "REPROVACAO",
    "ABANDONO",
}

DISCIPLINAS_SAEB = {
    "LP",
    "MT",
}

PADROES_PND = {
    "NAO_PROFICIENTE",
    "PADRAO_1",
    "PADRAO_2",
}

CORTE_BASICO_PND = 50.0
CORTE_ADEQUADO_PND = 70.0


def texto_limpo(
    serie,
):
    return (
        serie
        .astype("string")
        .str.strip()
    )


def inteiros(
    serie,
):
    return pd.to_numeric(
        serie,
        errors="raise",
    ).astype(
        "int64"
    )


def numericos(
    serie,
):
    return pd.to_numeric(
        serie,
        errors="coerce",
    )


def exigir_sem_ausencias(
    df,
    colunas,
    nome,
):
    ausencias = {
        coluna: int(
            df[
                coluna
            ].isna().sum()
        )
        for coluna in colunas
        if df[
            coluna
        ].isna().any()
    }

    if ausencias:
        raise RuntimeError(
            f"{nome}: valores ausentes encontrados: {ausencias}"
        )


def exigir_esquema(
    df,
    nome,
):
    esperado = COLUNAS_ESPERADAS[
        nome
    ]

    atual = list(
        df.columns
    )

    if atual != esperado:
        raise RuntimeError(
            f"{nome}: esquema diferente do esperado.\n"
            f"Esperado={esperado}\n"
            f"Atual={atual}"
        )


def exigir_linhas(
    df,
    nome,
):
    esperado = LINHAS_ESPERADAS[
        nome
    ]

    atual = len(
        df
    )

    if atual != esperado:
        raise RuntimeError(
            f"{nome}: linhas={atual:,}; esperado={esperado:,}."
        )


def exigir_chave_unica(
    df,
    colunas,
    nome,
):
    duplicadas = df.duplicated(
        subset=colunas,
        keep=False,
    )

    if duplicadas.any():
        exemplos = (
            df.loc[
                duplicadas,
                colunas,
            ]
            .head(20)
            .to_dict(
                orient="records"
            )
        )

        raise RuntimeError(
            f"{nome}: chave/grão duplicado em {colunas}. "
            f"Exemplos={exemplos}"
        )


def exigir_dominio_exato(
    serie,
    esperado,
    nome,
):
    atual = set(
        serie.dropna()
    )

    if atual != esperado:
        raise RuntimeError(
            f"{nome}: domínio inesperado.\n"
            f"Faltantes={sorted(esperado - atual)}\n"
            f"Extras={sorted(atual - esperado)}"
        )


def exigir_sem_orfas(
    fato,
    coluna_fato,
    dimensao,
    coluna_dimensao,
    nome,
):
    chaves_fato = set(
        fato[
            coluna_fato
        ].dropna()
    )

    chaves_dimensao = set(
        dimensao[
            coluna_dimensao
        ].dropna()
    )

    orfas = chaves_fato - chaves_dimensao

    if orfas:
        raise RuntimeError(
            f"{nome}: chaves órfãs encontradas: {sorted(orfas)}"
        )


def carregar_tabelas():
    ausentes = [
        str(
            caminho
        )
        for caminho in ARQUIVOS.values()
        if not caminho.exists()
    ]

    if ausentes:
        raise FileNotFoundError(
            "Arquivos Gold ausentes:\n"
            + "\n".join(
                ausentes
            )
        )

    tabelas = {
        nome: pd.read_parquet(
            caminho
        )
        for nome, caminho in ARQUIVOS.items()
    }

    return tabelas


def validar_dimensoes(
    tabelas,
):
    dim_uf = tabelas[
        "DIM_UF"
    ].copy()

    dim_tempo = tabelas[
        "DIM_TEMPO"
    ].copy()

    dim_etapa = tabelas[
        "DIM_ETAPA"
    ].copy()

    dim_area = tabelas[
        "DIM_AREA_PND"
    ].copy()

    dim_municipio = tabelas[
        "DIM_MUNICIPIO"
    ].copy()

    for nome, df in [
        ("DIM_UF", dim_uf),
        ("DIM_TEMPO", dim_tempo),
        ("DIM_ETAPA", dim_etapa),
        ("DIM_AREA_PND", dim_area),
        ("DIM_MUNICIPIO", dim_municipio),
    ]:
        exigir_esquema(
            df,
            nome,
        )

        exigir_linhas(
            df,
            nome,
        )

        exigir_sem_ausencias(
            df,
            list(
                df.columns
            ),
            nome,
        )

    dim_uf[
        "UF"
    ] = texto_limpo(
        dim_uf[
            "UF"
        ]
    )

    dim_tempo[
        "ANO"
    ] = inteiros(
        dim_tempo[
            "ANO"
        ]
    )

    dim_etapa[
        "ETAPA"
    ] = texto_limpo(
        dim_etapa[
            "ETAPA"
        ]
    )

    dim_etapa[
        "ORDEM_ETAPA"
    ] = inteiros(
        dim_etapa[
            "ORDEM_ETAPA"
        ]
    )

    dim_area[
        "CO_GRUPO"
    ] = inteiros(
        dim_area[
            "CO_GRUPO"
        ]
    )

    dim_area[
        "AREA_PROVA"
    ] = texto_limpo(
        dim_area[
            "AREA_PROVA"
        ]
    )

    dim_municipio[
        "CO_MUNICIPIO"
    ] = inteiros(
        dim_municipio[
            "CO_MUNICIPIO"
        ]
    )

    dim_municipio[
        "UF"
    ] = texto_limpo(
        dim_municipio[
            "UF"
        ]
    )

    exigir_chave_unica(
        dim_uf,
        [
            "UF",
        ],
        "DIM_UF",
    )

    exigir_chave_unica(
        dim_tempo,
        [
            "ANO",
        ],
        "DIM_TEMPO",
    )

    exigir_chave_unica(
        dim_etapa,
        [
            "ETAPA",
        ],
        "DIM_ETAPA",
    )

    exigir_chave_unica(
        dim_area,
        [
            "CO_GRUPO",
        ],
        "DIM_AREA_PND",
    )

    exigir_chave_unica(
        dim_municipio,
        [
            "CO_MUNICIPIO",
        ],
        "DIM_MUNICIPIO",
    )

    exigir_dominio_exato(
        dim_uf[
            "UF"
        ],
        UFS_ESPERADAS,
        "DIM_UF.UF",
    )

    exigir_dominio_exato(
        dim_tempo[
            "ANO"
        ],
        ANOS_DIM_TEMPO_ESPERADOS,
        "DIM_TEMPO.ANO",
    )

    exigir_dominio_exato(
        dim_etapa[
            "ETAPA"
        ],
        ETAPAS_ESPERADAS,
        "DIM_ETAPA.ETAPA",
    )

    ordem_atual = dict(
        zip(
            dim_etapa[
                "ETAPA"
            ],
            dim_etapa[
                "ORDEM_ETAPA"
            ],
        )
    )

    if ordem_atual != ORDEM_ETAPAS_ESPERADA:
        raise RuntimeError(
            "DIM_ETAPA: ORDEM_ETAPA divergente.\n"
            f"Esperado={ORDEM_ETAPAS_ESPERADA}\n"
            f"Atual={ordem_atual}"
        )

    if set(
        dim_municipio[
            "UF"
        ]
    ) - UFS_ESPERADAS:
        raise RuntimeError(
            "DIM_MUNICIPIO contém UF fora de DIM_UF."
        )

    return {
        "DIM_UF": dim_uf,
        "DIM_TEMPO": dim_tempo,
        "DIM_ETAPA": dim_etapa,
        "DIM_AREA_PND": dim_area,
        "DIM_MUNICIPIO": dim_municipio,
    }


def validar_fato_rendimento(
    fato,
):
    nome = "FATO_RENDIMENTO"

    exigir_esquema(
        fato,
        nome,
    )

    exigir_linhas(
        fato,
        nome,
    )

    exigir_sem_ausencias(
        fato,
        COLUNAS_ESPERADAS[
            nome
        ],
        nome,
    )

    fato = fato.copy()

    fato[
        "ANO"
    ] = inteiros(
        fato[
            "ANO"
        ]
    )

    for coluna in [
        "UF",
        "ETAPA",
        "REDE",
        "INDICADOR",
    ]:
        fato[
            coluna
        ] = texto_limpo(
            fato[
                coluna
            ]
        )

    fato[
        "VALOR"
    ] = numericos(
        fato[
            "VALOR"
        ]
    )

    exigir_chave_unica(
        fato,
        [
            "ANO",
            "UF",
            "ETAPA",
            "REDE",
            "INDICADOR",
        ],
        nome,
    )

    exigir_dominio_exato(
        fato[
            "ANO"
        ],
        ANOS_HISTORICOS_ANUAIS,
        f"{nome}.ANO",
    )

    exigir_dominio_exato(
        fato[
            "UF"
        ],
        UFS_ESPERADAS,
        f"{nome}.UF",
    )

    exigir_dominio_exato(
        fato[
            "ETAPA"
        ],
        ETAPAS_ESPERADAS,
        f"{nome}.ETAPA",
    )

    exigir_dominio_exato(
        fato[
            "REDE"
        ],
        {
            "PUBLICA",
        },
        f"{nome}.REDE",
    )

    exigir_dominio_exato(
        fato[
            "INDICADOR"
        ],
        INDICADORES_RENDIMENTO,
        f"{nome}.INDICADOR",
    )

    fora = (
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

    if fora.any():
        raise RuntimeError(
            f"{nome}: VALOR fora do domínio 0–100."
        )

    return fato


def validar_fato_tdi(
    fato,
):
    nome = "FATO_TDI"

    exigir_esquema(
        fato,
        nome,
    )

    exigir_linhas(
        fato,
        nome,
    )

    exigir_sem_ausencias(
        fato,
        COLUNAS_ESPERADAS[
            nome
        ],
        nome,
    )

    fato = fato.copy()

    fato[
        "ANO"
    ] = inteiros(
        fato[
            "ANO"
        ]
    )

    for coluna in [
        "UF",
        "ETAPA",
        "REDE",
    ]:
        fato[
            coluna
        ] = texto_limpo(
            fato[
                coluna
            ]
        )

    fato[
        "TDI"
    ] = numericos(
        fato[
            "TDI"
        ]
    )

    exigir_chave_unica(
        fato,
        [
            "ANO",
            "UF",
            "ETAPA",
            "REDE",
        ],
        nome,
    )

    exigir_dominio_exato(
        fato[
            "ANO"
        ],
        ANOS_HISTORICOS_ANUAIS,
        f"{nome}.ANO",
    )

    exigir_dominio_exato(
        fato[
            "UF"
        ],
        UFS_ESPERADAS,
        f"{nome}.UF",
    )

    exigir_dominio_exato(
        fato[
            "ETAPA"
        ],
        ETAPAS_ESPERADAS,
        f"{nome}.ETAPA",
    )

    exigir_dominio_exato(
        fato[
            "REDE"
        ],
        {
            "PUBLICA",
        },
        f"{nome}.REDE",
    )

    fora = (
        (
            fato[
                "TDI"
            ] < 0
        )
        | (
            fato[
                "TDI"
            ] > 100
        )
    )

    if fora.any():
        raise RuntimeError(
            f"{nome}: TDI fora do domínio 0–100."
        )

    return fato


def validar_fato_ideb(
    fato,
):
    nome = "FATO_IDEB"

    exigir_esquema(
        fato,
        nome,
    )

    exigir_linhas(
        fato,
        nome,
    )

    exigir_sem_ausencias(
        fato,
        COLUNAS_ESPERADAS[
            nome
        ],
        nome,
    )

    fato = fato.copy()

    fato[
        "ANO"
    ] = inteiros(
        fato[
            "ANO"
        ]
    )

    for coluna in [
        "UF",
        "ETAPA",
        "REDE",
    ]:
        fato[
            coluna
        ] = texto_limpo(
            fato[
                coluna
            ]
        )

    fato[
        "IDEB"
    ] = numericos(
        fato[
            "IDEB"
        ]
    )

    exigir_chave_unica(
        fato,
        [
            "ANO",
            "UF",
            "ETAPA",
            "REDE",
        ],
        nome,
    )

    exigir_dominio_exato(
        fato[
            "ANO"
        ],
        ANOS_BIENAIS,
        f"{nome}.ANO",
    )

    exigir_dominio_exato(
        fato[
            "UF"
        ],
        UFS_ESPERADAS,
        f"{nome}.UF",
    )

    exigir_dominio_exato(
        fato[
            "ETAPA"
        ],
        ETAPAS_ESPERADAS,
        f"{nome}.ETAPA",
    )

    exigir_dominio_exato(
        fato[
            "REDE"
        ],
        {
            "PUBLICA",
        },
        f"{nome}.REDE",
    )

    fora = (
        (
            fato[
                "IDEB"
            ] < 0
        )
        | (
            fato[
                "IDEB"
            ] > 10
        )
    )

    if fora.any():
        raise RuntimeError(
            f"{nome}: IDEB fora do domínio 0–10."
        )

    return fato


def validar_fato_saeb(
    fato,
):
    nome = "FATO_SAEB"

    exigir_esquema(
        fato,
        nome,
    )

    exigir_linhas(
        fato,
        nome,
    )

    exigir_sem_ausencias(
        fato,
        COLUNAS_ESPERADAS[
            nome
        ],
        nome,
    )

    fato = fato.copy()

    fato[
        "ANO"
    ] = inteiros(
        fato[
            "ANO"
        ]
    )

    for coluna in [
        "UF",
        "ETAPA",
        "REDE",
        "DISCIPLINA",
    ]:
        fato[
            coluna
        ] = texto_limpo(
            fato[
                coluna
            ]
        )

    fato[
        "PROFICIENCIA"
    ] = numericos(
        fato[
            "PROFICIENCIA"
        ]
    )

    exigir_chave_unica(
        fato,
        [
            "ANO",
            "UF",
            "ETAPA",
            "REDE",
            "DISCIPLINA",
        ],
        nome,
    )

    exigir_dominio_exato(
        fato[
            "ANO"
        ],
        ANOS_BIENAIS,
        f"{nome}.ANO",
    )

    exigir_dominio_exato(
        fato[
            "UF"
        ],
        UFS_ESPERADAS,
        f"{nome}.UF",
    )

    exigir_dominio_exato(
        fato[
            "ETAPA"
        ],
        ETAPAS_ESPERADAS,
        f"{nome}.ETAPA",
    )

    exigir_dominio_exato(
        fato[
            "REDE"
        ],
        {
            "PUBLICA",
        },
        f"{nome}.REDE",
    )

    exigir_dominio_exato(
        fato[
            "DISCIPLINA"
        ],
        DISCIPLINAS_SAEB,
        f"{nome}.DISCIPLINA",
    )

    fora = (
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

    if fora.any():
        raise RuntimeError(
            f"{nome}: PROFICIENCIA fora do domínio 0–500."
        )

    return fato


def classificar_pnd(
    nt_obj,
):
    return pd.Series(
        np.select(
            [
                nt_obj < CORTE_BASICO_PND,
                nt_obj < CORTE_ADEQUADO_PND,
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


def validar_fato_pnd(
    fato,
):
    nome = "FATO_PND"

    exigir_esquema(
        fato,
        nome,
    )

    exigir_linhas(
        fato,
        nome,
    )

    exigir_sem_ausencias(
        fato,
        COLUNAS_ESPERADAS[
            nome
        ],
        nome,
    )

    fato = fato.copy()

    fato[
        "ANO"
    ] = inteiros(
        fato[
            "ANO"
        ]
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
    ] = inteiros(
        fato[
            "CO_MUNICIPIO_PROVA"
        ]
    )

    fato[
        "CO_GRUPO"
    ] = inteiros(
        fato[
            "CO_GRUPO"
        ]
    )

    for coluna in [
        "PROFICIENCIA",
        "NT_OBJ",
        "NT_DIS",
        "NT_GER",
        "QT_ACERTOS",
    ]:
        fato[
            coluna
        ] = numericos(
            fato[
                coluna
            ]
        )

    fato[
        "PADRAO_DESEMPENHO"
    ] = texto_limpo(
        fato[
            "PADRAO_DESEMPENHO"
        ]
    )

    exigir_dominio_exato(
        fato[
            "ANO"
        ],
        {
            2025,
        },
        f"{nome}.ANO",
    )

    exigir_dominio_exato(
        fato[
            "UF_PROVA"
        ],
        UFS_ESPERADAS,
        f"{nome}.UF_PROVA",
    )

    exigir_dominio_exato(
        fato[
            "PADRAO_DESEMPENHO"
        ],
        PADROES_PND,
        f"{nome}.PADRAO_DESEMPENHO",
    )

    nt_obj = fato[
        "NT_OBJ"
    ]

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
            f"{nome}: NT_OBJ fora da escala oficial 0–100."
        )

    if (
        fato[
            "QT_ACERTOS"
        ] < 0
    ).any():
        raise RuntimeError(
            f"{nome}: QT_ACERTOS negativo."
        )

    esperado = classificar_pnd(
        nt_obj
    )

    if not fato[
        "PADRAO_DESEMPENHO"
    ].equals(
        esperado
    ):
        raise RuntimeError(
            f"{nome}: PADRAO_DESEMPENHO diverge dos cortes oficiais."
        )

    if fato[
        "CO_GRUPO"
    ].nunique() != 17:
        raise RuntimeError(
            f"{nome}: quantidade de áreas diferente de 17."
        )

    if fato[
        "CO_MUNICIPIO_PROVA"
    ].nunique() != 750:
        raise RuntimeError(
            f"{nome}: quantidade de municípios diferente de 750."
        )

    return fato


def validar_integridade_referencial(
    dimensoes,
    fatos,
):
    dim_uf = dimensoes[
        "DIM_UF"
    ]

    dim_tempo = dimensoes[
        "DIM_TEMPO"
    ]

    dim_etapa = dimensoes[
        "DIM_ETAPA"
    ]

    dim_area = dimensoes[
        "DIM_AREA_PND"
    ]

    dim_municipio = dimensoes[
        "DIM_MUNICIPIO"
    ]

    historicas = [
        "FATO_RENDIMENTO",
        "FATO_TDI",
        "FATO_IDEB",
        "FATO_SAEB",
    ]

    for nome in historicas:
        fato = fatos[
            nome
        ]

        exigir_sem_orfas(
            fato,
            "UF",
            dim_uf,
            "UF",
            f"{nome} → DIM_UF",
        )

        exigir_sem_orfas(
            fato,
            "ANO",
            dim_tempo,
            "ANO",
            f"{nome} → DIM_TEMPO",
        )

        exigir_sem_orfas(
            fato,
            "ETAPA",
            dim_etapa,
            "ETAPA",
            f"{nome} → DIM_ETAPA",
        )

    pnd = fatos[
        "FATO_PND"
    ]

    exigir_sem_orfas(
        pnd,
        "UF_PROVA",
        dim_uf,
        "UF",
        "FATO_PND → DIM_UF",
    )

    exigir_sem_orfas(
        pnd,
        "ANO",
        dim_tempo,
        "ANO",
        "FATO_PND → DIM_TEMPO",
    )

    exigir_sem_orfas(
        pnd,
        "CO_GRUPO",
        dim_area,
        "CO_GRUPO",
        "FATO_PND → DIM_AREA_PND",
    )

    exigir_sem_orfas(
        pnd,
        "CO_MUNICIPIO_PROVA",
        dim_municipio,
        "CO_MUNICIPIO",
        "FATO_PND → DIM_MUNICIPIO",
    )

    pares_fato = (
        pnd[
            [
                "CO_MUNICIPIO_PROVA",
                "UF_PROVA",
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    pares_dim = (
        dim_municipio[
            [
                "CO_MUNICIPIO",
                "UF",
            ]
        ]
        .copy()
    )

    teste = pares_fato.merge(
        pares_dim,
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
            "FATO_PND: CO_MUNICIPIO_PROVA e UF_PROVA "
            "divergem de DIM_MUNICIPIO."
        )


def validar_reproducao_das_dimensoes(
    dimensoes,
    fatos,
):
    ufs_fatos = set()

    for nome in [
        "FATO_RENDIMENTO",
        "FATO_TDI",
        "FATO_IDEB",
        "FATO_SAEB",
    ]:
        ufs_fatos.update(
            fatos[
                nome
            ][
                "UF"
            ].dropna()
        )

    ufs_fatos.update(
        fatos[
            "FATO_PND"
        ][
            "UF_PROVA"
        ].dropna()
    )

    if ufs_fatos != set(
        dimensoes[
            "DIM_UF"
        ][
            "UF"
        ]
    ):
        raise RuntimeError(
            "DIM_UF não corresponde exatamente às UFs utilizadas pelas fatos."
        )

    anos_fatos = set()

    for fato in fatos.values():
        anos_fatos.update(
            fato[
                "ANO"
            ].dropna().astype(
                int
            )
        )

    if anos_fatos != set(
        dimensoes[
            "DIM_TEMPO"
        ][
            "ANO"
        ].astype(
            int
        )
    ):
        raise RuntimeError(
            "DIM_TEMPO não corresponde exatamente aos anos utilizados pelas fatos."
        )

    etapas_fatos = set()

    for nome in [
        "FATO_RENDIMENTO",
        "FATO_TDI",
        "FATO_IDEB",
        "FATO_SAEB",
    ]:
        etapas_fatos.update(
            fatos[
                nome
            ][
                "ETAPA"
            ].dropna()
        )

    if etapas_fatos != set(
        dimensoes[
            "DIM_ETAPA"
        ][
            "ETAPA"
        ]
    ):
        raise RuntimeError(
            "DIM_ETAPA não corresponde exatamente às etapas utilizadas pelas fatos."
        )

    grupos_fato = set(
        fatos[
            "FATO_PND"
        ][
            "CO_GRUPO"
        ].dropna().astype(
            int
        )
    )

    grupos_dim = set(
        dimensoes[
            "DIM_AREA_PND"
        ][
            "CO_GRUPO"
        ].dropna().astype(
            int
        )
    )

    if grupos_fato != grupos_dim:
        raise RuntimeError(
            "DIM_AREA_PND não corresponde exatamente aos grupos utilizados na FATO_PND."
        )

    municipios_fato = set(
        fatos[
            "FATO_PND"
        ][
            "CO_MUNICIPIO_PROVA"
        ].dropna().astype(
            int
        )
    )

    municipios_dim = set(
        dimensoes[
            "DIM_MUNICIPIO"
        ][
            "CO_MUNICIPIO"
        ].dropna().astype(
            int
        )
    )

    if municipios_fato != municipios_dim:
        raise RuntimeError(
            "DIM_MUNICIPIO não corresponde exatamente aos municípios utilizados na FATO_PND."
        )


def main():
    print("=" * 118)
    print(
        "VALIDAÇÃO GLOBAL — CAMADA GOLD"
    )
    print("=" * 118)
    print()

    print(
        "1/5 Verificando e lendo todas as tabelas Gold..."
    )

    tabelas = carregar_tabelas()

    print(
        "2/5 Validando dimensões, chaves e domínios..."
    )

    dimensoes = validar_dimensoes(
        tabelas
    )

    print(
        "3/5 Validando fatos, grãos e domínios analíticos..."
    )

    fatos = {
        "FATO_RENDIMENTO": validar_fato_rendimento(
            tabelas[
                "FATO_RENDIMENTO"
            ]
        ),
        "FATO_TDI": validar_fato_tdi(
            tabelas[
                "FATO_TDI"
            ]
        ),
        "FATO_IDEB": validar_fato_ideb(
            tabelas[
                "FATO_IDEB"
            ]
        ),
        "FATO_SAEB": validar_fato_saeb(
            tabelas[
                "FATO_SAEB"
            ]
        ),
        "FATO_PND": validar_fato_pnd(
            tabelas[
                "FATO_PND"
            ]
        ),
    }

    print(
        "4/5 Validando integridade referencial do modelo dimensional..."
    )

    validar_integridade_referencial(
        dimensoes,
        fatos,
    )

    print(
        "5/5 Confirmando que as dimensões reproduzem exatamente os domínios usados pelas fatos..."
    )

    validar_reproducao_das_dimensoes(
        dimensoes,
        fatos,
    )

    contagens_pnd = (
        fatos[
            "FATO_PND"
        ][
            "PADRAO_DESEMPENHO"
        ]
        .value_counts()
        .to_dict()
    )

    proficientes = (
        contagens_pnd.get(
            "PADRAO_1",
            0,
        )
        + contagens_pnd.get(
            "PADRAO_2",
            0,
        )
    )

    percentual_proficientes = (
        proficientes
        / len(
            fatos[
                "FATO_PND"
            ]
        )
        * 100
    )

    print()
    print(
        "DIMENSÕES"
    )
    print(
        f"DIM_UF: {len(dimensoes['DIM_UF']):,} | chave única: OK"
    )
    print(
        f"DIM_TEMPO: {len(dimensoes['DIM_TEMPO']):,} | chave única: OK"
    )
    print(
        f"DIM_ETAPA: {len(dimensoes['DIM_ETAPA']):,} | chave única: OK"
    )
    print(
        f"DIM_AREA_PND: {len(dimensoes['DIM_AREA_PND']):,} | chave única: OK"
    )
    print(
        f"DIM_MUNICIPIO: {len(dimensoes['DIM_MUNICIPIO']):,} | chave única: OK"
    )
    print()
    print(
        "FATOS"
    )
    print(
        f"FATO_RENDIMENTO: {len(fatos['FATO_RENDIMENTO']):,} | grão: OK"
    )
    print(
        f"FATO_TDI: {len(fatos['FATO_TDI']):,} | grão: OK"
    )
    print(
        f"FATO_IDEB: {len(fatos['FATO_IDEB']):,} | grão: OK"
    )
    print(
        f"FATO_SAEB: {len(fatos['FATO_SAEB']):,} | grão: OK"
    )
    print(
        f"FATO_PND: {len(fatos['FATO_PND']):,} | grão individual preservado"
    )
    print()
    print(
        "INTEGRIDADE REFERENCIAL"
    )
    print(
        "Fatos históricas → DIM_UF / DIM_TEMPO / DIM_ETAPA: OK"
    )
    print(
        "FATO_PND → DIM_UF / DIM_TEMPO / DIM_AREA_PND / DIM_MUNICIPIO: OK"
    )
    print(
        "Coerência CO_MUNICIPIO_PROVA → UF_PROVA: OK"
    )
    print(
        "Dimensões = domínios efetivamente utilizados pelas fatos: OK"
    )
    print()
    print(
        "PND — PADRÃO OFICIAL DE DESEMPENHO"
    )
    print(
        f"Não proficientes: {contagens_pnd.get('NAO_PROFICIENTE', 0):,}"
    )
    print(
        f"Padrão 1: {contagens_pnd.get('PADRAO_1', 0):,}"
    )
    print(
        f"Padrão 2: {contagens_pnd.get('PADRAO_2', 0):,}"
    )
    print(
        f"Proficientes: {proficientes:,} ({percentual_proficientes:.2f}%)"
    )
    print()
    print(
        "MODELO DIMENSIONAL GOLD: OK"
    )
    print("=" * 118)


if __name__ == "__main__":
    main()
