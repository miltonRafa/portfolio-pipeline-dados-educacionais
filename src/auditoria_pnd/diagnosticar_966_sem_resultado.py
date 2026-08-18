from pathlib import Path
import pandas as pd


ARQUIVO = Path(
    "data/raw/pnd/microdados2025_pnd_arq1.txt"
)

COLUNAS = [
    "CO_GRUPO",
    "CO_MUNICIPIO_PROVA",
    "SG_UF_MUNICIPIO_PROVA",
    "TP_INSCRICAO_PND",
    "IN_REAPLICACAO",
    "CO_CADERNO",
    "TP_PRES",
    "TP_SIT_DISC",
    "DS_VT_ESC_OBJ",
    "DS_VT_ACE_OBJ",
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
]


partes = []


for chunk in pd.read_csv(
    ARQUIVO,
    sep=";",
    decimal=",",
    na_values=["NA"],
    usecols=COLUNAS,
    chunksize=100_000,
    low_memory=False,
    encoding="utf-8"
):

    sem_resultado = chunk[
        (chunk["TP_PRES"] == 555)
        & chunk["PROFICIENCIA"].isna()
        & chunk["NT_OBJ"].isna()
        & chunk["NT_DIS"].isna()
        & chunk["NT_GER"].isna()
        & chunk["QT_ACERTOS"].isna()
    ].copy()

    if not sem_resultado.empty:
        partes.append(sem_resultado)


dados = pd.concat(
    partes,
    ignore_index=True
)


print("=" * 110)
print("DIAGNÓSTICO — TP_PRES=555 SEM RESULTADOS")
print("=" * 110)

print(f"\nTOTAL: {len(dados):,}")


def mostrar_contagem(coluna):

    print("\n" + coluna)
    print("-" * 70)

    print(
        dados[coluna]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )


for coluna in [
    "TP_SIT_DISC",
    "TP_INSCRICAO_PND",
    "IN_REAPLICACAO",
    "CO_CADERNO",
    "CO_GRUPO",
    "SG_UF_MUNICIPIO_PROVA",
]:
    mostrar_contagem(coluna)


print("\n" + "=" * 110)
print("VETORES DA PROVA OBJETIVA")
print("=" * 110)

print("\nDS_VT_ESC_OBJ ausente:")
print(
    dados["DS_VT_ESC_OBJ"]
    .isna()
    .value_counts()
    .to_string()
)

print("\nDS_VT_ACE_OBJ ausente:")
print(
    dados["DS_VT_ACE_OBJ"]
    .isna()
    .value_counts()
    .to_string()
)


print("\n" + "=" * 110)
print("PRIMEIROS 20 CASOS")
print("=" * 110)

print(
    dados[
        [
            "CO_GRUPO",
            "SG_UF_MUNICIPIO_PROVA",
            "TP_INSCRICAO_PND",
            "IN_REAPLICACAO",
            "CO_CADERNO",
            "TP_SIT_DISC",
            "DS_VT_ESC_OBJ",
            "DS_VT_ACE_OBJ",
        ]
    ]
    .head(20)
    .to_string(index=False)
)