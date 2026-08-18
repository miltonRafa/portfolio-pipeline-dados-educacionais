from pathlib import Path
import pandas as pd


ARQUIVO = Path(
    "data/raw/pnd/microdados2025_pnd_arq1.txt"
)

COLUNAS = [
    "NU_ANO",
    "CO_GRUPO",
    "SG_UF_MUNICIPIO_PROVA",
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
]


print("=" * 110)
print("AUDITORIA ESTRUTURAL — MICRODADOS PND 2025")
print("=" * 110)


# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------

cabecalho = pd.read_csv(
    ARQUIVO,
    sep=";",
    nrows=0,
    encoding="utf-8"
)

print("\nTOTAL DE COLUNAS:")
print(len(cabecalho.columns))

print("\nCOLUNAS:")
for coluna in cabecalho.columns:
    print(f"- {coluna}")


# ---------------------------------------------------------
# Acumuladores
# ---------------------------------------------------------

total_registros = 0

anos = set()
grupos = set()
ufs = set()

categorias = {
    "TP_INSCRICAO_PND": set(),
    "IN_REAPLICACAO": set(),
    "CO_CADERNO": set(),
    "TP_PRES": set(),
    "TP_SIT_DISC": set(),
}

campos_numericos = [
    "PROFICIENCIA",
    "NT_OBJ",
    "NT_DIS",
    "NT_GER",
    "QT_ACERTOS",
]

validos = {
    coluna: 0
    for coluna in campos_numericos
}

ausentes = {
    coluna: 0
    for coluna in campos_numericos
}


# ---------------------------------------------------------
# Leitura em chunks
# ---------------------------------------------------------

for numero_chunk, chunk in enumerate(
    pd.read_csv(
        ARQUIVO,
        sep=";",
        decimal=",",
        na_values=["NA"],
        usecols=COLUNAS,
        chunksize=100_000,
        low_memory=False,
        encoding="utf-8"
    ),
    start=1
):

    total_registros += len(chunk)

    anos.update(
        chunk["NU_ANO"]
        .dropna()
        .unique()
        .tolist()
    )

    grupos.update(
        chunk["CO_GRUPO"]
        .dropna()
        .unique()
        .tolist()
    )

    ufs.update(
        chunk["SG_UF_MUNICIPIO_PROVA"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    for coluna in categorias:

        categorias[coluna].update(
            chunk[coluna]
            .dropna()
            .unique()
            .tolist()
        )

    for coluna in campos_numericos:

        validos[coluna] += (
            chunk[coluna]
            .notna()
            .sum()
        )

        ausentes[coluna] += (
            chunk[coluna]
            .isna()
            .sum()
        )

    print(
        f"Chunk {numero_chunk}: "
        f"{len(chunk):,} registros"
    )


# ---------------------------------------------------------
# Resultado
# ---------------------------------------------------------

print("\n" + "=" * 110)
print("RESULTADO")
print("=" * 110)

print(f"\nTOTAL DE REGISTROS: {total_registros:,}")

print("\nANOS:")
print(sorted(anos))

print("\nTOTAL DE GRUPOS:")
print(len(grupos))

print("GRUPOS:")
print(sorted(grupos))

print("\nTOTAL DE UFs:")
print(len(ufs))

print("UFs:")
print(sorted(ufs))


for coluna, valores in categorias.items():

    print(f"\n{coluna}:")
    print(sorted(valores, key=str))


print("\nCOBERTURA DOS CAMPOS NUMÉRICOS:")

for coluna in campos_numericos:

    print(
        f"{coluna}: "
        f"{validos[coluna]:,} válidos | "
        f"{ausentes[coluna]:,} ausentes"
    )