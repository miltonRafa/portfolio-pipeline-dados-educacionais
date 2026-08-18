from pathlib import Path
import re
import unicodedata

import pandas as pd


BRONZE_DIR = Path("data/bronze/rendimento")

CONFIG = {
    2007: {"cabecalho_indice": 6, "linhas": 480, "colunas_fonte": 59},
    2008: {"cabecalho_indice": 6, "linhas": 480, "colunas_fonte": 58},
    2009: {"cabecalho_indice": 6, "linhas": 483, "colunas_fonte": 58},
    2010: {"cabecalho_indice": 6, "linhas": 483, "colunas_fonte": 58},
    2011: {"cabecalho_indice": 6, "linhas": 486, "colunas_fonte": 58},
    2012: {"cabecalho_indice": 6, "linhas": 486, "colunas_fonte": 58},
    2013: {"cabecalho_indice": 6, "linhas": 486, "colunas_fonte": 58},
    2014: {"cabecalho_indice": 6, "linhas": 486, "colunas_fonte": 58},
    2015: {"cabecalho_indice": 6, "linhas": 489, "colunas_fonte": 58},
    2016: {"cabecalho_indice": 5, "linhas": 487, "colunas_fonte": 59},
    2017: {"cabecalho_indice": 5, "linhas": 595, "colunas_fonte": 58},
    2018: {"cabecalho_indice": 5, "linhas": 595, "colunas_fonte": 58},
    2019: {"cabecalho_indice": 5, "linhas": 595, "colunas_fonte": 58},
    2020: {"cabecalho_indice": 5, "linhas": 595, "colunas_fonte": 58},
    2021: {"cabecalho_indice": 5, "linhas": 595, "colunas_fonte": 58},
    2022: {"cabecalho_indice": 5, "linhas": 595, "colunas_fonte": 58},
    2023: {"cabecalho_indice": 5, "linhas": 596, "colunas_fonte": 58},
}

TERMOS = {
    "rede": [
        "federal",
        "estadual",
        "municipal",
        "publica",
        "privada",
    ],
    "localizacao": [
        "urbana",
        "rural",
        "total",
    ],
    "etapa": [
        "anos iniciais",
        "anos finais",
        "ensino fundamental",
        "1 ao 5",
        "6 ao 9",
        "1o ao 5o",
        "6o ao 9o",
    ],
    "indicador": [
        "aprov",
        "reprov",
        "aband",
        "rendimento",
    ],
}


def normalizar(valor):
    texto = "" if pd.isna(valor) else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )
    return texto.casefold().strip()


def colunas_fonte(df):
    colunas = [
        coluna
        for coluna in df.columns
        if re.fullmatch(r"col_\d{3}", coluna)
    ]

    return sorted(
        colunas,
        key=lambda coluna: int(coluna.split("_")[1]),
    )


def validar_basico(ano, df, config, fontes):
    if len(df) != config["linhas"]:
        raise RuntimeError(
            f"Rendimento {ano}: linhas diferentes da Bronze validada. "
            f"Esperado={config['linhas']}, atual={len(df)}"
        )

    if len(fontes) != config["colunas_fonte"]:
        raise RuntimeError(
            f"Rendimento {ano}: colunas fonte diferentes da Bronze validada. "
            f"Esperado={config['colunas_fonte']}, atual={len(fontes)}"
        )

    indices = (
        df["_indice_cabecalho_origem"]
        .dropna()
        .unique()
        .tolist()
    )

    if indices != [config["cabecalho_indice"]]:
        raise RuntimeError(
            f"Rendimento {ano}: _indice_cabecalho_origem inesperado. "
            f"Esperado={[config['cabecalho_indice']]}, atual={indices}"
        )


def mostrar_linhas_estruturais(ano, df, fontes, cabecalho_indice):
    linha_cabecalho = cabecalho_indice + 1
    inicio = max(1, linha_cabecalho - 2)
    fim = linha_cabecalho + 8

    print()
    print("LINHAS ESTRUTURAIS E PRIMEIROS REGISTROS")
    print("-" * 110)

    for numero in range(inicio, fim + 1):
        linha = df.loc[
            df["_linha_origem"] == numero,
            fontes,
        ]

        if linha.empty:
            print(
                f"_linha_origem={numero}: <linha ausente ou removida por ser totalmente vazia>"
            )
            continue

        valores = []

        for coluna in fontes:
            valor = linha.iloc[0][coluna]

            if pd.isna(valor):
                continue

            texto = str(valor)

            if texto.strip() == "":
                continue

            valores.append(
                f"{coluna}={texto!r}"
            )

        if valores:
            print(
                f"_linha_origem={numero}: "
                + " | ".join(valores)
            )
        else:
            print(
                f"_linha_origem={numero}: <sem valores substantivos>"
            )


def localizar_termos(df, fontes):
    print()
    print("VALORES SEMÂNTICOS LOCALIZADOS")
    print("-" * 110)

    for grupo, termos in TERMOS.items():
        encontrados = []

        for coluna in fontes:
            serie = df[coluna].dropna()

            for valor in serie.unique():
                texto = str(valor).strip()

                if not texto:
                    continue

                normalizado = normalizar(texto)

                if any(
                    termo in normalizado
                    for termo in termos
                ):
                    item = (coluna, texto)

                    if item not in encontrados:
                        encontrados.append(item)

        print(f"{grupo.upper()}:")

        if not encontrados:
            print("  <nenhum valor localizado>")
            continue

        for coluna, valor in encontrados[:40]:
            print(
                f"  {coluna}: {valor!r}"
            )

        if len(encontrados) > 40:
            print(
                f"  ... {len(encontrados) - 40} ocorrências únicas adicionais"
            )


def mostrar_amostra_final(df, fontes):
    print()
    print("AMOSTRA DOS 3 PRIMEIROS REGISTROS COM MAIOR DENSIDADE DE VALORES")
    print("-" * 110)

    trabalho = df[["_linha_origem", *fontes]].copy()

    trabalho["_qtd_preenchidos"] = (
        trabalho[fontes]
        .notna()
        .sum(axis=1)
    )

    candidatos = (
        trabalho.sort_values(
            ["_qtd_preenchidos", "_linha_origem"],
            ascending=[False, True],
        )
        .head(3)
    )

    for _, linha in candidatos.iterrows():
        numero = int(linha["_linha_origem"])

        valores = []

        for coluna in fontes:
            valor = linha[coluna]

            if pd.isna(valor):
                continue

            texto = str(valor)

            if texto.strip() == "":
                continue

            valores.append(
                f"{coluna}={texto!r}"
            )

        print(
            f"_linha_origem={numero}: "
            + " | ".join(valores)
        )


def main():
    print("=" * 110)
    print("AUDITORIA PARA A CAMADA SILVER — RENDIMENTO ESCOLAR")
    print("=" * 110)

    for ano, config in CONFIG.items():
        caminho = (
            BRONZE_DIR
            / f"rendimento_{ano}.parquet"
        )

        if not caminho.exists():
            raise FileNotFoundError(
                f"Parquet Bronze ausente: {caminho}"
            )

        df = pd.read_parquet(
            caminho
        )

        fontes = colunas_fonte(
            df
        )

        validar_basico(
            ano=ano,
            df=df,
            config=config,
            fontes=fontes,
        )

        print()
        print("=" * 110)
        print(f"RENDIMENTO {ano}")
        print("=" * 110)
        print(f"Arquivo Bronze: {caminho.name}")
        print(f"Linhas Bronze: {len(df):,}")
        print(f"Colunas fonte: {len(fontes)}")
        print(
            "_indice_cabecalho_origem: "
            f"{config['cabecalho_indice']}"
        )
        print(
            "_linha_origem correspondente ao início do cabeçalho: "
            f"{config['cabecalho_indice'] + 1}"
        )

        mostrar_linhas_estruturais(
            ano=ano,
            df=df,
            fontes=fontes,
            cabecalho_indice=config["cabecalho_indice"],
        )

        localizar_termos(
            df=df,
            fontes=fontes,
        )

        mostrar_amostra_final(
            df=df,
            fontes=fontes,
        )

    print()
    print("=" * 110)
    print("AUDITORIA CONCLUÍDA.")
    print(
        "Nenhum arquivo Bronze ou Silver foi alterado."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
