import pandas as pd
from pathlib import Path

arquivos = {
    2007: Path("data/raw/saeb/Dicionario_SAEB_2007.xlsx"),
    2009: Path("data/raw/saeb/Dicionario_SAEB_2009.xlsx"),
    2023: Path("data/raw/saeb/Dicionario_Saeb_2023.xlsx"),
}

termos = [
    "IN_PUBLICA",
    "ID_UF",
    "CO_UF",
    "ID_LOCALIZACAO",
    "NU_PRESENTES",
    "MEDIA_",
]

for ano, arquivo in arquivos.items():

    print("\n" + "=" * 100)
    print(f"ANO {ano}")
    print("=" * 100)

    excel = pd.ExcelFile(arquivo)

    print("ABAS:")
    for aba in excel.sheet_names:
        print(f"- {aba}")

    for aba in excel.sheet_names:

        df = pd.read_excel(
            arquivo,
            sheet_name=aba,
            header=None
        )

        texto = df.astype(str)

        mascara = texto.apply(
            lambda coluna: coluna.str.contains(
                "|".join(termos),
                case=False,
                regex=True,
                na=False
            )
        ).any(axis=1)

        resultado = df[mascara]

        if not resultado.empty:
            print("\n" + "-" * 80)
            print(f"ABA: {aba}")
            print("-" * 80)

            print(
                resultado.to_string(
                    index=False,
                    header=False
                )
            )