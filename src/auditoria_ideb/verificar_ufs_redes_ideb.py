import pandas as pd
from pathlib import Path

arquivo = Path(
    "data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx"
)

abas = {
    "AI": "UF e Regiões (AI)",
    "AF": "UF e Regiões (AF)",
}

ufs = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "R. G. do Norte", "Paraíba",
    "Pernambuco", "Alagoas", "Sergipe", "Bahia",
    "Minas Gerais", "Espírito Santo", "Rio de Janeiro", "São Paulo",
    "Paraná", "Santa Catarina", "R. G. do Sul",
    "M. G. do Sul", "Mato Grosso", "Goiás", "Distrito Federal",
]

nomes_canonicos = {
    "R. G. do Norte": "Rio Grande do Norte",
    "R. G. do Sul": "Rio Grande do Sul",
    "M. G. do Sul": "Mato Grosso do Sul",
}

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
    df["UF_CANONICA"] = df["UF"].replace(nomes_canonicos)

    print("\nQUANTIDADE DE UFs ENCONTRADAS:")
    print(df["UF_CANONICA"].nunique())

    print("\nUFs ENCONTRADAS:")
    print(sorted(df["UF_CANONICA"].unique()))

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

        nome = nomes_canonicos.get(uf, uf)
        print(f"{nome}: {redes}")
