from pathlib import Path
import pandas as pd

from config_auditoria_saeb import SAEB


def ler_csv(caminho):
    """Tenta ler CSV detectando separador e encoding."""
    encodings = ["utf-8", "latin1", "cp1252"]

    for encoding in encodings:
        try:
            return pd.read_csv(
                caminho,
                sep=None,
                engine="python",
                encoding=encoding,
                nrows=5
            )
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Não foi possível identificar o encoding de {caminho}")


def inspecionar_saeb():
    for ano, caminho in SAEB.items():
        print("\n" + "=" * 100)
        print(f"ANO: {ano}")
        print(f"ARQUIVO: {caminho}")
        print("=" * 100)

        if not caminho.exists():
            print("ERRO: arquivo não encontrado.")
            continue

        extensao = caminho.suffix.lower()

        try:
            if extensao in [".xlsx", ".xls"]:
                excel = pd.ExcelFile(caminho)

                print("ABAS:")
                for aba in excel.sheet_names:
                    print(f"  - {aba}")

                for aba in excel.sheet_names:
                    print(f"\n--- ABA: {aba} ---")

                    df = pd.read_excel(
                        caminho,
                        sheet_name=aba,
                        nrows=5
                    )

                    print("\nCOLUNAS:")
                    for coluna in df.columns:
                        print(f"  {coluna}")

                    print("\nPRIMEIRAS LINHAS:")
                    print(df.head().to_string(index=False))

            elif extensao == ".csv":
                df = ler_csv(caminho)

                print("\nCOLUNAS:")
                for coluna in df.columns:
                    print(f"  {coluna}")

                print("\nPRIMEIRAS LINHAS:")
                print(df.head().to_string(index=False))

            else:
                print(f"Formato ainda não tratado: {extensao}")

        except Exception as erro:
            print(f"ERRO AO LER: {erro}")


if __name__ == "__main__":
    inspecionar_saeb()