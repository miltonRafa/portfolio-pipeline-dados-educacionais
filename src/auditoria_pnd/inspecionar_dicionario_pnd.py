from pathlib import Path
import pandas as pd


ARQUIVO = Path(
    "data/raw/pnd/Dicionário_arquivos_variáveis_PND_2025.xlsx"
)


print("=" * 100)
print("DICIONÁRIO PND 2025")
print("=" * 100)


try:

    excel = pd.ExcelFile(
        ARQUIVO,
        engine="calamine"
    )

    print("\nABAS ENCONTRADAS:")

    for aba in excel.sheet_names:
        print(f"- {aba}")

    print(f"\nTOTAL DE ABAS: {len(excel.sheet_names)}")

    for aba in excel.sheet_names:

        print("\n" + "=" * 100)
        print(f"ABA: {aba}")
        print("=" * 100)

        df = pd.read_excel(
            ARQUIVO,
            sheet_name=aba,
            engine="calamine",
            header=None,
            nrows=40
        )

        print(
            df.to_string(
                index=True,
                header=False
            )
        )

except Exception as erro:

    print("\nERRO AO LER COM CALAMINE:")
    print(repr(erro))