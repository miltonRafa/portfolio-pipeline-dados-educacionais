from pathlib import Path
import zipfile


ARQUIVO = Path(
    "data/raw/pnd/Dicionário_arquivos_variáveis_PND_2025.xlsx"
)


print("=" * 100)
print("DIAGNÓSTICO DO ARQUIVO DO DICIONÁRIO")
print("=" * 100)

print(f"\nArquivo: {ARQUIVO.name}")
print(f"Tamanho: {ARQUIVO.stat().st_size:,} bytes")

with open(ARQUIVO, "rb") as f:
    primeiros = f.read(32)

print("\nPRIMEIROS 32 BYTES:")
print(primeiros)

print("\nÉ ZIP/XLSX VÁLIDO?")
print(zipfile.is_zipfile(ARQUIVO))


if zipfile.is_zipfile(ARQUIVO):

    print("\nCONTEÚDO INTERNO DO ZIP:")

    with zipfile.ZipFile(ARQUIVO, "r") as z:

        nomes = z.namelist()

        for nome in nomes[:100]:
            print(nome)

        print(f"\nTOTAL DE ARQUIVOS INTERNOS: {len(nomes)}")

        print("\nPOSSUI workbook.xml?")
        print("xl/workbook.xml" in nomes)

        print("\nPOSSUI worksheets?")
        worksheets = [
            x for x in nomes
            if x.startswith("xl/worksheets/")
        ]

        print(worksheets)