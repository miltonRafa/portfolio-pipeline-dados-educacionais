from pathlib import Path

import pandas as pd


ARQUIVO = Path(
    "data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb"
)


def texto(valor):
    if pd.isna(valor):
        return ""

    return str(valor).strip()


def linha_compacta(linha):
    partes = []

    for indice, valor in linha.items():
        valor = texto(valor)

        if valor:
            partes.append(
                f"c{int(indice) + 1:03d}={valor!r}"
            )

    return " | ".join(partes)


def main():
    print("=" * 120)
    print(
        "AUDITORIA — RESULTADOS OFICIAIS DO SAEB 2023"
    )
    print("=" * 120)
    print()

    if not ARQUIVO.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO}"
        )

    print(f"Arquivo: {ARQUIVO}")
    print(
        f"Tamanho: {ARQUIVO.stat().st_size:,} bytes"
    )
    print()

    try:
        excel = pd.ExcelFile(
            ARQUIVO,
            engine="pyxlsb",
        )
    except ImportError as exc:
        raise RuntimeError(
            "O pacote 'pyxlsb' é necessário para ler o arquivo .xlsb. "
            "Instale no mesmo ambiente Python do projeto com: "
            "python -m pip install pyxlsb"
        ) from exc

    print("ABAS ENCONTRADAS")
    print("-" * 120)

    for indice, aba in enumerate(
        excel.sheet_names,
        start=1,
    ):
        print(
            f"{indice:>2}. {aba!r}"
        )

    print()
    print("=" * 120)
    print(
        "AMOSTRA ESTRUTURAL DAS ABAS"
    )
    print("=" * 120)

    for aba in excel.sheet_names:
        print()
        print("-" * 120)
        print(f"ABA: {aba!r}")
        print("-" * 120)

        try:
            amostra = pd.read_excel(
                ARQUIVO,
                sheet_name=aba,
                header=None,
                nrows=25,
                engine="pyxlsb",
                dtype=object,
            )
        except Exception as exc:
            print(
                f"[ERRO] Não foi possível ler a aba: {exc}"
            )
            continue

        linhas_exibidas = 0

        for indice, linha in amostra.iterrows():
            compacta = linha_compacta(
                linha
            )

            if not compacta:
                continue

            print(
                f"linha_excel={indice + 1:>3}: "
                f"{compacta}"
            )

            linhas_exibidas += 1

        if linhas_exibidas == 0:
            print(
                "<nenhuma célula preenchida nas primeiras 25 linhas>"
            )

    print()
    print("=" * 120)
    print(
        "AUDITORIA CONCLUÍDA."
    )
    print(
        "Nenhum arquivo foi alterado."
    )
    print("=" * 120)


if __name__ == "__main__":
    main()
