import pandas as pd
from pathlib import Path

arquivo = Path(
    "data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx"
)

abas = [
    "UF e Regiões (AI)",
    "UF e Regiões (AF)",
]

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 300)

for aba in abas:

    print("\n" + "=" * 100)
    print("ABA:", aba)
    print("=" * 100)

    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None
    )

    print(f"\nTOTAL DE LINHAS: {len(df)}")
    print("\nÚLTIMAS 25 LINHAS:")
    print(
        df.tail(25).to_string(
            index=True,
            header=False
        )
    )
