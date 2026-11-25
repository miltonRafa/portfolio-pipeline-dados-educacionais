from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

if not __package__:  # Execução direta pelo pipeline.
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.referencias_pnd import ler_areas_oficiais



BRONZE_FILE = Path(
    "data/bronze/pnd/pnd_2025.parquet"
)

SILVER_FILE = Path(
    "data/silver/pnd/pnd_2025.parquet"
)

TOTAL_DADOS_ESPERADO = 1_087_359
TOTAL_RESULTADOS_COMPLETOS_ESPERADO = 759_152
TOTAL_POPULACAO_ANALITICA_ESPERADO = 759_140
TOTAL_555_ESPERADO = 760_106
TOTAL_555_SEM_RESULTADO_ESPERADO = 966
TOTAL_888_COM_RESULTADO_ESPERADO = 12

UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF",
    "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
    "RO", "RR", "SC", "SP", "SE", "TO",
}

CAMPOS_RESULTADO = [
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
]

CAMPOS_FONTE = [
    "NU_ANO", "CO_GRUPO", "CO_MUNICIPIO_PROVA", "SG_UF_MUNICIPIO_PROVA",
    "TP_INSCRICAO_PND", "IN_REAPLICACAO", "CO_CADERNO", "TP_PRES",
    "TP_SIT_DISC", *CAMPOS_RESULTADO,
]

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


def ler_dados_bronze(caminho):
    # Ler todos os rótulos antes de projetar as colunas: uma duplicata pode
    # estar inclusive em uma coluna que a Silver não consome.
    with pq.ParquetFile(caminho) as parquet:
        primeiro = next(parquet.iter_batches(batch_size=1), None)
        if primeiro is None:
            raise RuntimeError("Bronze da PND vazia.")
        linha = primeiro.to_pylist()[0]
        if linha["_linha_origem"] != 1 or linha["_indice_cabecalho_origem"] != 0:
            raise RuntimeError("Cabeçalho físico da PND não encontrado na primeira linha.")
        nomes = {}
        for coluna, rotulo in linha.items():
            if coluna.startswith("col_") and rotulo in CAMPOS_FONTE:
                if rotulo in nomes.values():
                    raise RuntimeError(f"Cabeçalho ambíguo na Bronze PND: {rotulo}.")
                nomes[coluna] = rotulo
        faltantes = set(CAMPOS_FONTE).difference(nomes.values())
        if faltantes:
            raise RuntimeError(f"Campos ausentes no cabeçalho da PND: {sorted(faltantes)}.")
        metadados = ["_linha_origem", "_arquivo_origem", "_granularidade_origem",
                     "_indice_cabecalho_origem"]
        bronze = parquet.read(columns=[*nomes, *metadados]).to_pandas().rename(columns=nomes)
    if not bronze["_indice_cabecalho_origem"].eq(0).fillna(False).all():
        raise RuntimeError("Índice de cabeçalho divergente na Bronze PND.")
    if bronze["_linha_origem"].eq(1).sum() != 1:
        raise RuntimeError("Cabeçalho físico da PND não é único.")
    return bronze.iloc[1:]


def reconstruir_referencia(dados):
    if len(dados) != TOTAL_DADOS_ESPERADO:
        raise RuntimeError(
            f"Registros Bronze={len(dados):,}; "
            f"esperado={TOTAL_DADOS_ESPERADO:,}."
        )

    # A completude é apurada pelos cinco valores numéricos publicados.
    # Um zero é um resultado. O TXT publicado usa NA para ausência.
    resultados = pd.DataFrame(index=dados.index)
    for campo in CAMPOS_RESULTADO:
        valores = dados[campo].str.strip()
        valores = valores.mask(valores.str.upper().isin(["", "NA", "."]))
        resultados[campo] = pd.to_numeric(valores.str.replace(",", ".", regex=False), errors="raise")
    preenchidos = resultados.notna().sum(axis=1)
    completos = preenchidos.eq(len(CAMPOS_RESULTADO))
    presente = dados["TP_PRES"].eq("555").fillna(False)
    elegiveis = presente & completos

    contagens = {
        "presentes": int(presente.sum()),
        "completos": int(completos.sum()),
        "parciais": int((preenchidos.gt(0) & ~completos).sum()),
        "555_completo": int(elegiveis.sum()),
        "555_incompleto": int((presente & ~completos).sum()),
        "888_completo": int((dados["TP_PRES"].eq("888") & completos).sum()),
    }

    esperado = {
        "presentes": TOTAL_555_ESPERADO,
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

    selecionados = dados.loc[elegiveis]

    referencia = pd.DataFrame(
        index=selecionados.index
    )

    referencia[
        "ANO"
    ] = inteiro(
        selecionados[
            "NU_ANO"
        ],
        "NU_ANO",
    )

    referencia[
        "CO_GRUPO"
    ] = inteiro(
        selecionados[
            "CO_GRUPO"
        ],
        "CO_GRUPO",
    )

    referencia[
        "AREA_PROVA"
    ] = referencia[
        "CO_GRUPO"
    ].map(
        ler_areas_oficiais()
    ).astype(
        "string"
    )

    if referencia["AREA_PROVA"].isna().any():
        codigos = referencia.loc[referencia["AREA_PROVA"].isna(), "CO_GRUPO"].unique()
        raise RuntimeError(f"CO_GRUPO ausente no dicionário oficial: {codigos.tolist()}.")

    referencia[
        "CO_MUNICIPIO_PROVA"
    ] = inteiro(
        selecionados[
            "CO_MUNICIPIO_PROVA"
        ],
        "CO_MUNICIPIO_PROVA",
    )

    referencia[
        "UF_PROVA"
    ] = (
        texto_limpo(
            selecionados[
                "SG_UF_MUNICIPIO_PROVA"
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
                campo
            ],
            campo,
        )

    referencia[CAMPOS_RESULTADO] = resultados.loc[elegiveis, CAMPOS_RESULTADO]
    referencia["QT_ACERTOS"] = referencia["QT_ACERTOS"].astype("Int64")

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
    ].eq(555).fillna(False).all():
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



def validar_nota_geral(silver):
    # NT 44/2025, itens 7.3, 8.1 e 9.2. No arquivo de 2025, NT_GER
    # é publicada com até duas casas: admitir meia unidade da última casa.
    calculada = 0.8 * silver["NT_OBJ"] + 2 * silver["NT_DIS"]
    consistente = np.isclose(silver["NT_GER"].to_numpy(dtype=float),
                             calculada.to_numpy(dtype=float), rtol=0, atol=0.005 + 1e-12)
    if not consistente.all():
        pos = np.flatnonzero(~consistente)[0]
        linha = silver.iloc[pos]
        raise RuntimeError(
            f"NT_GER incompatível com a Nota Técnica 44/2025 na linha Bronze "
            f"{linha['LINHA_ORIGEM_BRONZE']}: NT_OBJ={linha['NT_OBJ']}, "
            f"NT_DIS={linha['NT_DIS']}, NT_GER publicada={linha['NT_GER']}, "
            f"calculada={calculada.iloc[pos]}."
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

    referencia = reconstruir_referencia(ler_dados_bronze(BRONZE_FILE))

    print(
        "4/4 Comparando os 759.140 registros Silver ↔ Bronze..."
    )

    comparar(silver, referencia)
    validar_nota_geral(silver)
    print("Consistência da nota geral publicada (Nota Técnica 44/2025): OK")

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
