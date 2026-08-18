from pathlib import Path
import pandas as pd
import re


PASTA = Path("data/raw/tdi")


arquivos = sorted(
    [
        arquivo
        for arquivo in PASTA.iterdir()
        if arquivo.suffix.lower() in {".xls", ".xlsx"}
    ],
    key=lambda arquivo: (
        int(re.search(r"20\d{2}", arquivo.name).group())
        if re.search(r"20\d{2}", arquivo.name)
        else 9999,
        arquivo.name
    )
)


if not arquivos:
    raise FileNotFoundError(
        f"Nenhum arquivo Excel encontrado em: {PASTA}"
    )


pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)
pd.set_option("display.max_colwidth", 100)


print("\n" + "=" * 120)
print("ARQUIVOS TDI ENCONTRADOS")
print("=" * 120)

for arquivo in arquivos:
    print(f"- {arquivo.name}")

print(f"\nTOTAL: {len(arquivos)} arquivos")


for arquivo in arquivos:

    print("\n\n" + "#" * 120)
    print(f"ARQUIVO: {arquivo.name}")
    print("#" * 120)

    try:

        excel = pd.ExcelFile(arquivo)

        print("\nABAS:")

        for aba in excel.sheet_names:
            print(f"- {aba}")

        for aba in excel.sheet_names:

            print("\n" + "=" * 120)
            print(f"ABA: {aba}")
            print("=" * 120)

            df = pd.read_excel(
                arquivo,
                sheet_name=aba,
                header=None,
                nrows=18
            )

            print(
                df.to_string(
                    index=True,
                    header=False
                )
            )

    except Exception as erro:

        print("\nERRO AO LER O ARQUIVO:")
        print(repr(erro))