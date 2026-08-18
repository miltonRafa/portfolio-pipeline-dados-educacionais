import pandas as pd
from config import SAEB


for ano, caminho in SAEB.items():

    print("\n" + "=" * 80)
    print(f"ANO {ano}")
    print("=" * 80)

    try:
        if caminho.suffix.lower() == ".csv":
            df = pd.read_csv(
                caminho,
                sep=None,
                engine="python",
                encoding="latin1"
            )
        else:
            # 2013 e 2015 serão tratados separadamente depois
            if ano in [2013, 2015]:
                print("Cabeçalho especial - verificar depois.")
                continue

            df = pd.read_excel(caminho)

        colunas_verificar = [
            "DEPENDENCIA_ADM",
            "LOCALIZACAO",
            "CAPITAL",
            "ID_TIPO_REDE",
            "ID_LOCALIZACAO",
            "ID_CAPITAL",
            "ID_SERIE"
        ]

        for coluna in colunas_verificar:
            if coluna in df.columns:
                print(f"\n{coluna}:")
                print(df[coluna].dropna().unique())

    except Exception as erro:
        print(f"ERRO: {erro}")