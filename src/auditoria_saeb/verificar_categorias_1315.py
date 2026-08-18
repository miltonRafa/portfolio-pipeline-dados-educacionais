import pandas as pd
from config_auditoria_saeb import SAEB

configuracao = {
    2013: {
        "aba": "UF",
        "skiprows": 6,
    },
    2015: {
        "aba": "UFs",
        "skiprows": 5,
    },
}

colunas = [
    "UF",
    "REDE",
    "LOCALIZACAO",
    "CAPITAL",
    "LP_INICIAIS",
    "MT_INICIAIS",
    "LP_FINAIS",
    "MT_FINAIS",
    "LP_MEDIO",
    "MT_MEDIO",
]

for ano, cfg in configuracao.items():

    df = pd.read_excel(
        SAEB[ano],
        sheet_name=cfg["aba"],
        skiprows=cfg["skiprows"],
        header=None,
        names=colunas,
        usecols="A:J",
    )

    print("\n" + "=" * 80)
    print(f"ANO {ano}")
    print("=" * 80)

    print("\nREDE:")
    print(df["REDE"].dropna().unique())

    print("\nLOCALIZACAO:")
    print(df["LOCALIZACAO"].dropna().unique())

    print("\nCAPITAL:")
    print(df["CAPITAL"].dropna().unique())