import pandas as pd
from config import SAEB

for ano in [2013, 2015]:

    caminho = SAEB[ano]

    print("\n" + "=" * 100)
    print(f"ANO {ano}")
    print("=" * 100)

    excel = pd.ExcelFile(caminho)

    aba = excel.sheet_names[0]

    print("ABA:", aba)

    df = pd.read_excel(
        caminho,
        sheet_name=aba,
        header=None,
        nrows=12
    )

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 250)

    print(df.to_string(index=True, header=False))