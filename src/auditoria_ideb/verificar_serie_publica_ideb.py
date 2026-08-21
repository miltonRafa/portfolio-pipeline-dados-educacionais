import pandas as pd
from pathlib import Path

arquivo = Path(
    "data/raw/ideb/divulgacao_regioes_ufs_ideb.xlsx"
)

abas = {
    "AI": "UF e Regiões (AI)",
    "AF": "UF e Regiões (AF)",
}

mapa_ufs = {
    "R. G. do Norte": "Rio Grande do Norte",
    "R. G. do Sul": "Rio Grande do Sul",
    "M. G. do Sul": "Mato Grosso do Sul",
}

ufs_validas = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba",
    "Pernambuco", "Alagoas", "Sergipe", "Bahia",
    "Minas Gerais", "Espírito Santo", "Rio de Janeiro", "São Paulo",
    "Paraná", "Santa Catarina", "Rio Grande do Sul",
    "Mato Grosso do Sul", "Mato Grosso", "Goiás", "Distrito Federal",
]

anos = [
    2007,
    2009,
    2011,
    2013,
    2015,
    2017,
    2019,
    2021,
    2023,
]

for etapa, aba in abas.items():

    print("\n" + "=" * 100)
    print(f"ETAPA: {etapa} | ABA: {aba}")
    print("=" * 100)

    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=9
    )

    df = df.rename(
        columns={
            df.columns[0]: "UF",
            df.columns[1]: "REDE",
        }
    )

    df["UF"] = df["UF"].replace(mapa_ufs)

    # Somente as 27 UFs
    df = df[df["UF"].isin(ufs_validas)].copy()

    # Somente rede pública
    publica = df[
        df["REDE"]
        .astype(str)
        .str.startswith("Pública", na=False)
    ].copy()

    print("\nQUANTIDADE DE UFs NA REDE PÚBLICA:")
    print(publica["UF"].nunique())

    print("\nVERIFICAÇÃO POR ANO:")

    for ano in anos:

        coluna = f"VL_OBSERVADO_{ano}"

        if coluna not in publica.columns:
            print(f"{ano}: COLUNA NÃO ENCONTRADA")
            continue

        valores = publica[coluna].replace("-", pd.NA)

        total_validos = valores.notna().sum()
        total_ausentes = valores.isna().sum()

        print(
            f"{ano}: "
            f"{total_validos} válidos | "
            f"{total_ausentes} ausentes"
        )

        if total_ausentes > 0:
            print("  UFs sem valor:")

            for uf in publica.loc[valores.isna(), "UF"]:
                print(f"  - {uf}")

    print("\nUFs:")
    print(sorted(publica["UF"].dropna().unique()))
