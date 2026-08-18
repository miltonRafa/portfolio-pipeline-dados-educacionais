from pathlib import Path
import re

import pandas as pd


BRONZE_DIR = Path("data/bronze/tdi")

ANOS = list(range(2007, 2024))

CONFIG = {
    2007: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2008: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2009: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2010: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2011: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2012: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2013: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2014: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2015: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2016: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2017: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2018: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2019: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2020: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2021: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2022: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
    2023: {"linhas_bronze": None, "colunas_fonte": None, "cabecalho_indice": 5},
}

TERMOS = {
    "REDE": [
        "public",
        "federal",
        "estadual",
        "municipal",
        "privad",
        "particular",
        "depend",
        "rede",
    ],
    "LOCALIZACAO": [
        "total",
        "urbana",
        "rural",
        "localiza",
    ],
    "ETAPA": [
        "anos iniciais",
        "anos finais",
        "1º ao 5º",
        "6º ao 9º",
        "1ª a 4ª",
        "5ª a 8ª",
        "fundamental",
    ],
    "INDICADOR": [
        "distor",
        "idade",
        "serie",
        "série",
        "tdi",
        "taxa",
    ],
}


def colunas_fonte(df):
    return sorted(
        [
            coluna
            for coluna in df.columns
            if re.fullmatch(r"col_\d{3}", str(coluna))
        ]
    )


def formatar_linha(linha, colunas):
    partes = []

    for coluna in colunas:
        valor = linha[coluna]

        if pd.isna(valor):
            continue

        texto = str(valor).strip()

        if not texto:
            continue

        partes.append(
            f"{coluna}={texto!r}"
        )

    if not partes:
        return "<linha sem valores de fonte>"

    return " | ".join(partes)


def linha_por_origem(df, numero):
    if "_linha_origem" not in df.columns:
        return None

    encontrado = df[
        df["_linha_origem"] == numero
    ]

    if encontrado.empty:
        return None

    return encontrado.iloc[0]


def procurar_termos(df, colunas, termos):
    encontrados = {}

    for coluna in colunas:
        serie = (
            df[coluna]
            .dropna()
            .astype(str)
            .str.strip()
        )

        if serie.empty:
            continue

        mascara = pd.Series(
            False,
            index=serie.index,
        )

        for termo in termos:
            mascara = (
                mascara
                | serie.str.contains(
                    termo,
                    case=False,
                    regex=False,
                    na=False,
                )
            )

        valores = (
            serie[mascara]
            .drop_duplicates()
            .tolist()
        )

        if valores:
            encontrados[coluna] = valores

    return encontrados


def imprimir_encontrados(titulo, encontrados, limite=35):
    print(f"{titulo}:")

    if not encontrados:
        print("  <nenhuma ocorrência localizada>")
        return

    quantidade = 0

    for coluna, valores in encontrados.items():
        for valor in valores:
            print(
                f"  {coluna}: {valor!r}"
            )
            quantidade += 1

            if quantidade >= limite:
                restantes = sum(
                    len(v)
                    for v in encontrados.values()
                ) - quantidade

                if restantes > 0:
                    print(
                        f"  ... {restantes} ocorrências únicas adicionais"
                    )
                return


def amostra_densa(df, colunas, quantidade=3):
    dados = df.copy()

    densidade = (
        dados[colunas]
        .notna()
        .sum(axis=1)
    )

    candidatos = (
        dados.assign(
            _densidade=densidade
        )
        .sort_values(
            ["_densidade", "_linha_origem"],
            ascending=[False, True],
        )
        .head(quantidade)
    )

    return candidatos


def auditar_ano(ano):
    caminho = (
        BRONZE_DIR
        / f"tdi_{ano}.parquet"
    )

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo Bronze ausente: {caminho}"
        )

    df = pd.read_parquet(
        caminho
    )

    cols = colunas_fonte(
        df
    )

    if not cols:
        raise RuntimeError(
            f"TDI {ano}: nenhuma coluna col_### localizada."
        )

    indices = (
        df["_indice_cabecalho_origem"]
        .dropna()
        .unique()
        .tolist()
    )

    if len(indices) != 1:
        raise RuntimeError(
            f"TDI {ano}: _indice_cabecalho_origem não é único: {indices}"
        )

    indice = int(
        indices[0]
    )

    esperado = CONFIG[ano][
        "cabecalho_indice"
    ]

    if indice != esperado:
        raise RuntimeError(
            f"TDI {ano}: índice de cabeçalho inesperado. "
            f"Esperado={esperado}; atual={indice}."
        )

    inicio_cabecalho = (
        indice + 1
    )

    print("=" * 110)
    print(
        f"TDI {ano}"
    )
    print("=" * 110)
    print(
        f"Arquivo Bronze: {caminho.name}"
    )
    print(
        f"Linhas Bronze: {len(df):,}"
    )
    print(
        f"Colunas fonte: {len(cols)}"
    )
    print(
        f"_indice_cabecalho_origem: {indice}"
    )
    print(
        "_linha_origem correspondente ao início do cabeçalho: "
        f"{inicio_cabecalho}"
    )
    print()

    print(
        "LINHAS ESTRUTURAIS E PRIMEIROS REGISTROS"
    )
    print("-" * 110)

    for numero in range(
        max(1, inicio_cabecalho - 2),
        inicio_cabecalho + 7,
    ):
        linha = linha_por_origem(
            df,
            numero,
        )

        if linha is None:
            print(
                f"_linha_origem={numero}: "
                "<linha ausente ou removida por ser totalmente vazia>"
            )
            continue

        print(
            f"_linha_origem={numero}: "
            f"{formatar_linha(linha, cols)}"
        )

    print()
    print(
        "VALORES SEMÂNTICOS LOCALIZADOS"
    )
    print("-" * 110)

    for titulo, termos in TERMOS.items():
        encontrados = procurar_termos(
            df=df,
            colunas=cols,
            termos=termos,
        )

        imprimir_encontrados(
            titulo=titulo,
            encontrados=encontrados,
        )

    print()
    print(
        "AMOSTRA DOS 3 PRIMEIROS REGISTROS COM MAIOR DENSIDADE DE VALORES"
    )
    print("-" * 110)

    candidatos = amostra_densa(
        df=df,
        colunas=cols,
        quantidade=3,
    )

    for _, linha in candidatos.iterrows():
        numero = linha[
            "_linha_origem"
        ]

        print(
            f"_linha_origem={numero}: "
            f"{formatar_linha(linha, cols)}"
        )

    print()


def main():
    print("=" * 110)
    print(
        "AUDITORIA PARA A CAMADA SILVER — DISTORÇÃO IDADE-SÉRIE (TDI)"
    )
    print("=" * 110)
    print()

    if set(CONFIG) != set(ANOS):
        raise RuntimeError(
            "CONFIG não corresponde exatamente a 2007–2023."
        )

    for ano in ANOS:
        auditar_ano(
            ano
        )

    print("=" * 110)
    print(
        "AUDITORIA CONCLUÍDA."
    )
    print(
        "Nenhum arquivo Bronze ou Silver foi alterado."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
