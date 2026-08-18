from pathlib import Path
import pandas as pd


PASTA = Path("data/raw/pnd")


print("\n" + "=" * 110)
print("ARQUIVOS PND ENCONTRADOS")
print("=" * 110)

arquivos = sorted(
    [arquivo for arquivo in PASTA.iterdir() if arquivo.is_file()],
    key=lambda x: x.name.lower()
)

for arquivo in arquivos:
    print(f"- {arquivo.name} | {arquivo.suffix} | {arquivo.stat().st_size:,} bytes")

print(f"\nTOTAL: {len(arquivos)} arquivos")


for arquivo in arquivos:

    print("\n\n" + "#" * 110)
    print(f"ARQUIVO: {arquivo.name}")
    print("#" * 110)

    sufixo = arquivo.suffix.lower()

    try:

        if sufixo in {".xlsx", ".xls"}:

            excel = pd.ExcelFile(arquivo)

            print("\nABAS:")
            for aba in excel.sheet_names:
                print(f"- {aba}")

            for aba in excel.sheet_names:

                print("\n" + "=" * 110)
                print(f"ABA: {aba}")
                print("=" * 110)

                df = pd.read_excel(
                    arquivo,
                    sheet_name=aba,
                    header=None,
                    nrows=20
                )

                print(df.to_string(index=True, header=False))

        elif sufixo in {".txt", ".csv"}:

            print("\nPRIMEIRAS 10 LINHAS:")

            with open(
                arquivo,
                "r",
                encoding="utf-8",
                errors="replace"
            ) as f:

                for numero in range(10):
                    linha = f.readline()

                    if not linha:
                        break

                    print(f"{numero + 1}: {linha.rstrip()}")

        else:
            print("\nFormato não inspecionado automaticamente.")

    except Exception as erro:
        print("\nERRO:")
        print(repr(erro))