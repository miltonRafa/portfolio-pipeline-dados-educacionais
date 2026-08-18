import pandas as pd
from pathlib import Path

arquivo = Path("data/raw/saeb/Dicionario_SAEB_2011.xlsx")

df = pd.read_excel(
    arquivo,
    sheet_name="TS_RESULTADO_UF",
    header=None
)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

print(df.head(40).to_string(index=False, header=False))