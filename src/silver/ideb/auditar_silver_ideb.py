from pathlib import Path
import re

import pandas as pd


BRONZE_DIR = Path("data/bronze/ideb")

ARQUIVOS = {
    "ANOS_INICIAIS": BRONZE_DIR / "ideb_ai.parquet",
    "ANOS_FINAIS": BRONZE_DIR / "ideb_af.parquet",
    "ENSINO_MEDIO": BRONZE_DIR / "ideb_em.parquet",
}

TERMOS = {
    "REDE": [
        "public",
        "estadual",
        "municipal",
        "privad",
        "federal",
        "rede",
    ],
    "GEOGRAFIA": [
        "brasil",
        "região",
        "regiao",
        "unidade da federação",
        "unidade da federacao",
        "uf",
        "rondônia",
        "rondonia",
        "distrito federal",
    ],
    "IDEB": [
        "ideb",
        "índice de desenvolvimento da educação básica",
        "indice de desenvolvimento da educacao basica",
    ],
    "ANO": [
        "2005",
        "2007",
        "2009",
        "2011",
        "2013",
        "2015",
        "2017",
        "2019",
        "2021",
        "2023",
        "20215",
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

        partes.append(f"{coluna}={texto!r}")

    if not partes:
        return "<linha sem valores de fonte>"

    return " | ".join(partes)


def linha_por_origem(df, numero):
    if "_linha_origem" not in df.columns:
        return None

    encontrado = df[df["_linha_origem"] == numero]

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

        mascara = pd.Series(False, index=serie.index)

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


def imprimir_encontrados(titulo, encontrados, limite=60):
    print(f"{titulo}:")

    if not encontrados:
        print("  <nenhuma ocorrência localizada>")
        return

    quantidade = 0

    for coluna, valores in encontrados.items():
        for valor in valores:
            print(f"  {coluna}: {valor!r}")
            quantidade += 1

            if quantidade >= limite:
                restantes = (
                    sum(len(v) for v in encontrados.values())
                    - quantidade
                )

                if restantes > 0:
                    print(
                        f"  ... {restantes} ocorrências únicas adicionais"
                    )
                return


def amostra_densa(df, colunas, quantidade=5):
    densidade = df[colunas].notna().sum(axis=1)

    return (
        df.assign(_densidade=densidade)
        .sort_values(
            ["_densidade", "_linha_origem"],
            ascending=[False, True],
        )
        .head(quantidade)
    )


def imprimir_valores_iniciais_por_coluna(
    df,
    colunas,
    limite_colunas=25,
):
    print("PRIMEIROS VALORES ÚNICOS POR COLUNA")
    print("-" * 110)

    for coluna in colunas[:limite_colunas]:
        valores = (
            df[coluna]
            .dropna()
            .astype(str)
            .str.strip()
        )

        unicos = []

        for valor in valores:
            if not valor:
                continue

            if valor not in unicos:
                unicos.append(valor)

            if len(unicos) >= 12:
                break

        print(f"{coluna}: {unicos}")

    if len(colunas) > limite_colunas:
        print(
            f"... {len(colunas) - limite_colunas} colunas fonte adicionais não exibidas nesta seção."
        )


def auditar_etapa(etapa, caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo Bronze ausente: {caminho}"
        )

    df = pd.read_parquet(caminho)

    cols = colunas_fonte(df)

    if not cols:
        raise RuntimeError(
            f"IDEB {etapa}: nenhuma coluna col_### localizada."
        )

    indices = (
        df["_indice_cabecalho_origem"]
        .dropna()
        .unique()
        .tolist()
    )

    if len(indices) != 1:
        raise RuntimeError(
            f"IDEB {etapa}: _indice_cabecalho_origem não é único: {indices}"
        )

    indice = int(indices[0])

    etapas_origem = []

    if "_etapa_origem" in df.columns:
        etapas_origem = (
            df["_etapa_origem"]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .tolist()
        )

    anos_referencia = []

    if "_ano_referencia" in df.columns:
        anos_referencia = (
            df["_ano_referencia"]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

    print("=" * 110)
    print(f"IDEB — {etapa}")
    print("=" * 110)
    print(f"Arquivo Bronze: {caminho.name}")
    print(f"Linhas Bronze: {len(df):,}")
    print(f"Colunas fonte: {len(cols)}")
    print(f"_indice_cabecalho_origem: {indice}")
    print(f"_ano_referencia: {anos_referencia}")
    print(f"_etapa_origem: {etapas_origem}")
    print()

    print("LINHAS ESTRUTURAIS E PRIMEIROS REGISTROS")
    print("-" * 110)

    for numero in range(
        max(1, indice - 3),
        indice + 8,
    ):
        linha = linha_por_origem(df, numero)

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
    print("VALORES SEMÂNTICOS LOCALIZADOS")
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
    imprimir_valores_iniciais_por_coluna(
        df=df,
        colunas=cols,
    )

    print()
    print(
        "AMOSTRA DOS 5 PRIMEIROS REGISTROS COM MAIOR DENSIDADE DE VALORES"
    )
    print("-" * 110)

    candidatos = amostra_densa(
        df=df,
        colunas=cols,
        quantidade=5,
    )

    for _, linha in candidatos.iterrows():
        numero = linha["_linha_origem"]

        print(
            f"_linha_origem={numero}: "
            f"{formatar_linha(linha, cols)}"
        )

    print()


def main():
    print("=" * 110)
    print("AUDITORIA PARA A CAMADA SILVER — IDEB")
    print("=" * 110)
    print()
    print(
        "Objetivo: identificar a estrutura efetiva da Bronze do IDEB antes da transformação Silver."
    )
    print(
        "Escopo analítico posterior: 2007–2023, 27 UFs, rede pública, Anos Iniciais e Anos Finais."
    )
    print(
        "O Ensino Médio é inspecionado apenas para documentar a estrutura da fonte e não integra o escopo histórico principal."
    )
    print()

    for etapa, caminho in ARQUIVOS.items():
        auditar_etapa(
            etapa=etapa,
            caminho=caminho,
        )

    print("=" * 110)
    print("AUDITORIA CONCLUÍDA.")
    print("Nenhum arquivo Bronze ou Silver foi alterado.")
    print("=" * 110)


if __name__ == "__main__":
    main()
