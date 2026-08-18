import pandas as pd
from pathlib import Path

arquivo = Path(
    "data/raw/ideb/divulgacao_regioes_ufs_ideb_2023.xlsx"
)

abas = [
    "UF e Regiões (AI)",
    "UF e Regiões (AF)",
]

for aba in abas:

    print("\n" + "=" * 100)
    print("ABA:", aba)
    print("=" * 100)

    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None,
        skiprows=10,
        usecols="A:B",
        names=["UF", "REDE"],
    )

    valores = df["UF"].dropna().astype(str).unique()

    print("\nTODOS OS VALORES GEOGRÁFICOS ENCONTRADOS:")
    for valor in valores:
        print(repr(valor))

    print("\nPOSSÍVEIS RIO GRANDE / MATO GROSSO DO SUL:")
    for valor in valores:
        normalizado = valor.casefold()

        if (
            "grande" in normalizado
            or "mato" in normalizado
            or "sul" in normalizado
        ):
            print(repr(valor))