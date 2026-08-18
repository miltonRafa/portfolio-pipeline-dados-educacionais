from pathlib import Path
import pandas as pd


ARQUIVO = Path(
    "data/raw/pnd/microdados2025_pnd_arq1.txt"
)

COLUNAS = [
    "CO_GRUPO",
    "SG_UF_MUNICIPIO_PROVA",
    "TP_PRES",
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

    validos = chunk[
        (chunk["TP_PRES"] == 555)
        & chunk["PROFICIENCIA"].notna()
        & chunk["NT_OBJ"].notna()
        & chunk["NT_DIS"].notna()
        & chunk["NT_GER"].notna()
        & chunk["QT_ACERTOS"].notna()
    ].copy()

    partes.append(validos)


dados = pd.concat(
    partes,
    ignore_index=True
)


print("=" * 110)
print("REPRODUÇÃO DOS INDICADORES — PND 2025")
print("=" * 110)


print(
    f"\nPARTICIPANTES ANALÍTICOS: "
    f"{len(dados):,}"
)


# =========================================================
# BRASIL
# =========================================================

print("\n" + "=" * 110)
print("BRASIL")
print("=" * 110)

for coluna in [
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
]:

    serie = dados[coluna]

    print(
        f"\n{coluna}:"
        f"\n  média   = {serie.mean():.4f}"
        f"\n  mediana = {serie.median():.4f}"
        f"\n  mínimo  = {serie.min():.4f}"
        f"\n  máximo  = {serie.max():.4f}"
    )


# =========================================================
# UF
# =========================================================

por_uf = (
    dados.groupby(
        "SG_UF_MUNICIPIO_PROVA"
    )
    .agg(
        PARTICIPANTES=("NT_GER", "size"),
        MEDIA_PROFICIENCIA=("PROFICIENCIA", "mean"),
        MEDIA_NT_OBJ=("NT_OBJ", "mean"),
        MEDIA_NT_DIS=("NT_DIS", "mean"),
        MEDIA_NT_GER=("NT_GER", "mean"),
        MEDIA_QT_ACERTOS=("QT_ACERTOS", "mean"),
    )
    .reset_index()
    .sort_values(
        "SG_UF_MUNICIPIO_PROVA"
    )
)


print("\n" + "=" * 110)
print("RESULTADOS POR UF")
print("=" * 110)

print(
    por_uf.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# =========================================================
# ÁREA
# =========================================================

por_area = (
    dados.groupby(
        "CO_GRUPO"
    )
    .agg(
        PARTICIPANTES=("NT_GER", "size"),
        MEDIA_PROFICIENCIA=("PROFICIENCIA", "mean"),
        MEDIA_NT_OBJ=("NT_OBJ", "mean"),
        MEDIA_NT_DIS=("NT_DIS", "mean"),
        MEDIA_NT_GER=("NT_GER", "mean"),
        MEDIA_QT_ACERTOS=("QT_ACERTOS", "mean"),
    )
    .reset_index()
    .sort_values(
        "CO_GRUPO"
    )
)


print("\n" + "=" * 110)
print("RESULTADOS POR ÁREA")
print("=" * 110)

print(
    por_area.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# =========================================================
# CONTROLES
# =========================================================

print("\n" + "=" * 110)
print("CONTROLES")
print("=" * 110)

print(
    f"\nSoma dos participantes por UF: "
    f"{por_uf['PARTICIPANTES'].sum():,}"
)

print(
    f"Soma dos participantes por área: "
    f"{por_area['PARTICIPANTES'].sum():,}"
)

print(
    f"Total analítico: "
    f"{len(dados):,}"
)