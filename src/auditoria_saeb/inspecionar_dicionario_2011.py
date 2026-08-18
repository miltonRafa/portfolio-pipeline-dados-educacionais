import pandas as pd
from pathlib import Path

arquivo = Path("data/raw/saeb/Dicionario_SAEB_2011.xlsx")

excel = pd.ExcelFile(arquivo)

print("ABAS:")
for aba in excel.sheet_names:
    print("-", aba)

for aba in excel.sheet_names:
    print("\n" + "=" * 80)
    print("ABA:", aba)
    print("=" * 80)

    df = pd.read_excel(arquivo, sheet_name=aba, header=None)

    # mostra apenas linhas que contenham termos relevantes
    mascara = df.astype(str).apply(
        lambda col: col.str.contains(
            "ID_TIPO_REDE|ID_LOCALIZACAO|ID_CAPITAL|ID_SERIE",
            case=False,
            regex=True,
            na=False
        )
    ).any(axis=1)

    resultado = df[mascara]

    if not resultado.empty:
        print(resultado.to_string(index=False, header=False))