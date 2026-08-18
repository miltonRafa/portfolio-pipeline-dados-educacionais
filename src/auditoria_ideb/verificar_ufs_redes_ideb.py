import pandas as pd
from pathlib import Path

arquivo = Path(
    "data/raw/ideb/divulgacao_regioes_ufs_ideb_2023.xlsx"
)

abas = {
    "AI": "UF e Regiões (AI)",
    "AF": "UF e Regiões (AF)",
}

ufs = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba",
    "Pernambuco", "Alagoas", "Sergipe", "Bahia",
    "Minas Gerais", "Espírito Santo", "Rio de Janeiro", "São Paulo",
    "Paraná", "Santa Catarina", "Rio Grande do Sul",
    "Mato Grosso do Sul", "Mato Grosso", "Goiás", "Distrito Federal",
]

for etapa, aba in abas.items():

    print("\n" + "=" * 100)
    print(f"ETAPA: {etapa} | ABA: {aba}")
    print("=" * 100)

    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None,
        skiprows=10,
        usecols="A:B",
        names=["UF", "REDE"],
    )

    df = df[df["UF"].isin(ufs)].copy()

    print("\nQUANTIDADE DE UFs ENCONTRADAS:")
    print(df["UF"].nunique())

    print("\nUFs ENCONTRADAS:")
    print(sorted(df["UF"].unique()))

    print("\nCATEGORIAS DE REDE NAS UFs:")
    print(sorted(df["REDE"].dropna().astype(str).unique()))

    print("\nQUANTIDADE DE REGISTROS POR REDE:")
    print(df["REDE"].value_counts(dropna=False))

    print("\nREDES POR UF:")
    for uf in ufs:
        redes = (
            df.loc[df["UF"] == uf, "REDE"]
            .dropna()
            .astype(str)
            .tolist()
        )

        print(f"{uf}: {redes}")