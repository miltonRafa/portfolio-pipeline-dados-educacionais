import pandas as pd
from pathlib import Path

arquivos = {
    2007: Path("data/raw/saeb/TS_ESCOLA_2007.csv"),
    2009: Path("data/raw/saeb/TS_ESCOLA_2009.csv"),
    2023: Path("data/raw/saeb/TS_ESCOLA_2023.csv"),
}

for ano, arquivo in arquivos.items():

    print("\n" + "=" * 80)
    print(f"ANO {ano}")
    print("=" * 80)

    # tenta os separadores/encodings mais comuns
    df = None

    for encoding in ["utf-8", "latin1", "cp1252"]:
        try:
            df = pd.read_csv(
                arquivo,
                sep=None,
                engine="python",
                encoding=encoding
            )
            break
        except Exception:
            pass

    if df is None:
        print("ERRO AO LER")
        continue

    print("\nIN_PUBLICA:")
    print(df["IN_PUBLICA"].value_counts(dropna=False).sort_index())

    print("\nID_LOCALIZACAO:")
    print(df["ID_LOCALIZACAO"].value_counts(dropna=False).sort_index())

    print("\nUFs:")
    print(sorted(df["ID_UF"].dropna().unique()))

    print("\nTOTAL DE REGISTROS:")
    print(len(df))