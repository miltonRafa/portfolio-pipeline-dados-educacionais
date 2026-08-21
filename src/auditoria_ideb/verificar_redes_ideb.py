import pandas as pd
from pathlib import Path

arquivo = Path(
    "data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx"
)

abas = [
    "UF e Regiões (AI)",
    "UF e Regiões (AF)",
]

for aba in abas:

    print("\n" + "=" * 100)
    print("ABA:", aba)
    print("=" * 100)

    # Na planilha, os dados começam após as linhas de cabeçalho.
    # Coluna A = Região/UF
    # Coluna B = Rede
    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None,
        skiprows=10,
        usecols="A:B",
        names=["UF_REGIAO", "REDE"],
    )

    print("\nCATEGORIAS DE REDE:")
    for valor in df["REDE"].dropna().astype(str).unique():
        print(repr(valor))
