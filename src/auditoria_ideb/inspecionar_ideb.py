import pandas as pd
from pathlib import Path

arquivo = Path(
    "data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx"
)

excel = pd.ExcelFile(arquivo)

print("\nABAS:")
for aba in excel.sheet_names:
    print(f"- {aba}")

for aba in excel.sheet_names:

    print("\n" + "=" * 100)
    print(f"ABA: {aba}")
    print("=" * 100)

    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None,
        nrows=20
    )

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 400)

    print(df.to_string(index=True, header=False))
