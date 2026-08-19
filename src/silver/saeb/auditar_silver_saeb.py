from pathlib import Path
import re
import unicodedata

import pandas as pd


BRONZE_DIR = Path("data/bronze/saeb")

ARQUIVOS = {
    2007: BRONZE_DIR / "saeb_2007.parquet",
    2009: BRONZE_DIR / "saeb_2009.parquet",
    2011: BRONZE_DIR / "saeb_2011.parquet",
    2013: BRONZE_DIR / "saeb_2013.parquet",
    2015: BRONZE_DIR / "saeb_2015.parquet",
    2017: BRONZE_DIR / "saeb_2017.parquet",
    2019: BRONZE_DIR / "saeb_2019.parquet",
    2021: BRONZE_DIR / "saeb_2021.parquet",
    2023: BRONZE_DIR / "saeb_2023.parquet",
}

UFS_NOME = {
    "acre",
    "alagoas",
    "amapa",
    "amazonas",
    "bahia",
    "ceara",
    "distrito federal",
    "espirito santo",
    "goias",
    "maranhao",
    "mato grosso",
    "mato grosso do sul",
    "minas gerais",
    "para",
    "paraiba",
    "parana",
    "pernambuco",
    "piaui",
    "rio de janeiro",
    "rio grande do norte",
    "rio grande do sul",
    "rondonia",
    "roraima",
    "santa catarina",
    "sao paulo",
    "sergipe",
    "tocantins",
}

UFS_SIGLA = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}

ESTRUTURA = {
    2007: {
        "uf": "col_003",
        "rede": "col_004",
        "localizacao": "col_005",
        "capital": "col_006",
        "metricas": {
            "AI_LP": "col_007",
            "AI_MT": "col_008",
            "AF_LP": "col_009",
            "AF_MT": "col_010",
        },
    },
    2009: {
        "uf": "col_003",
        "rede": "col_004",
        "localizacao": "col_005",
        "capital": "col_006",
        "metricas": {
            "AI_LP": "col_007",
            "AI_MT": "col_008",
            "AF_LP": "col_009",
            "AF_MT": "col_010",
        },
    },
    2011: {
        "uf": "col_003",
        "serie": "col_005",
        "rede": "col_006",
        "localizacao": "col_007",
        "capital": "col_008",
        "participantes": "col_009",
        "metricas": {
            "LP": "col_010",
            "MT": "col_011",
        },
    },
    2013: {
        "uf": "col_001",
        "rede": "col_002",
        "localizacao": "col_003",
        "capital": "col_004",
        "metricas": {
            "AI_LP": "col_005",
            "AI_MT": "col_006",
            "AF_LP": "col_007",
            "AF_MT": "col_008",
        },
    },
    2015: {
        "uf": "col_001",
        "rede": "col_002",
        "localizacao": "col_003",
        "capital": "col_004",
        "metricas": {
            "AI_LP": "col_005",
            "AI_MT": "col_006",
            "AF_LP": "col_007",
            "AF_MT": "col_008",
        },
    },
    2017: {
        "uf": "col_002",
        "rede": "col_003",
        "localizacao": "col_004",
        "capital": "col_005",
        "metricas": {
            "AI_LP": "col_006",
            "AI_MT": "col_007",
            "AF_LP": "col_008",
            "AF_MT": "col_009",
        },
    },
    2019: {
        "uf": "col_002",
        "rede": "col_003",
        "localizacao": "col_004",
        "capital": "col_005",
        "metricas": {
            "AI_LP": "col_008",
            "AI_MT": "col_009",
            "AF_LP": "col_010",
            "AF_MT": "col_011",
        },
    },
    2021: {
        "uf": "col_002",
        "rede": "col_003",
        "localizacao": "col_004",
        "capital": "col_005",
        "metricas": {
            "AI_LP": "col_008",
            "AI_MT": "col_009",
            "AF_LP": "col_010",
            "AF_MT": "col_011",
        },
    },
}


def normalizar(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )
    texto = re.sub(r"\s+", " ", texto)

    return texto.casefold()


def colunas_fonte(df):
    return sorted(
        coluna
        for coluna in df.columns
        if re.fullmatch(r"col_\d{3}", str(coluna))
    )


def cabecalho_origem(df, ano):
    valores = (
        df["_indice_cabecalho_origem"]
        .dropna()
        .unique()
        .tolist()
    )

    if len(valores) != 1:
        raise RuntimeError(
            f"{ano}: _indice_cabecalho_origem deveria ser único: {valores}"
        )

    return int(valores[0]) + 1


def linha_por_origem(df, numero):
    linha = df[
        df["_linha_origem"] == numero
    ]

    if linha.empty:
        return None

    return linha.iloc[0]


def formatar_linha(linha, colunas, limite=35):
    if linha is None:
        return "<linha ausente>"

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

        if len(partes) >= limite:
            partes.append("...")
            break

    return " | ".join(partes) if partes else "<sem valores>"


def dados_uf(df, ano):
    if ano == 2011:
        return df[
            df["col_003"]
            .astype("string")
            .str.strip()
            .isin(UFS_SIGLA)
        ].copy()

    estrutura = ESTRUTURA.get(ano)

    if estrutura is None:
        return df.copy()

    coluna = estrutura["uf"]

    return df[
        df[coluna]
        .map(normalizar)
        .isin(UFS_NOME)
    ].copy()


def imprimir_frequencia(titulo, serie, limite=30):
    print(f"{titulo}:")

    valores = (
        serie
        .dropna()
        .astype(str)
        .str.strip()
    )
    valores = valores[
        valores != ""
    ]

    if valores.empty:
        print("  <sem valores>")
        return

    contagem = (
        valores.value_counts()
        .head(limite)
    )

    for valor, quantidade in contagem.items():
        print(
            f"  {valor!r}: {quantidade}"
        )


def mostrar_estrutura_conhecida(df, ano):
    estrutura = ESTRUTURA[ano]
    dados = dados_uf(df, ano)

    print("ESTRUTURA ANALÍTICA CONFIRMADA/TESTADA")
    print("-" * 120)
    print(f"UF: {estrutura['uf']}")
    print(f"REDE: {estrutura['rede']}")
    print(f"LOCALIZAÇÃO: {estrutura['localizacao']}")
    print(f"CAPITAL: {estrutura['capital']}")

    if "serie" in estrutura:
        print(f"SÉRIE: {estrutura['serie']}")

    if "participantes" in estrutura:
        print(
            f"PARTICIPANTES: {estrutura['participantes']}"
        )

    for nome, coluna in estrutura["metricas"].items():
        print(
            f"{nome}: {coluna}"
        )

    print()
    print(
        f"Linhas pertencentes às 27 UFs: {len(dados):,}"
    )

    imprimir_frequencia(
        "REDE",
        dados[estrutura["rede"]],
    )

    imprimir_frequencia(
        "LOCALIZAÇÃO",
        dados[estrutura["localizacao"]],
    )

    imprimir_frequencia(
        "CAPITAL",
        dados[estrutura["capital"]],
    )

    if "serie" in estrutura:
        imprimir_frequencia(
            "SÉRIE",
            dados[estrutura["serie"]],
        )

    print()


def mapa_cabecalho_2023(df, ano):
    origem = cabecalho_origem(
        df,
        ano,
    )

    linha = linha_por_origem(
        df,
        origem,
    )

    if linha is None:
        raise RuntimeError(
            f"{ano}: linha de cabeçalho de origem {origem} não encontrada."
        )

    mapa = {}

    for coluna in colunas_fonte(df):
        valor = linha[coluna]

        if pd.isna(valor):
            continue

        texto = str(valor).strip()

        if texto:
            mapa[coluna] = texto

    return origem, mapa


def procurar_no_mapa(mapa, padroes):
    resultado = []

    for coluna, nome in mapa.items():
        texto = normalizar(nome)

        if any(
            re.search(padrao, texto)
            for padrao in padroes
        ):
            resultado.append(
                (
                    coluna,
                    nome,
                )
            )

    return resultado


def coluna_exata(mapa, nomes):
    alvos = {
        normalizar(nome)
        for nome in nomes
    }

    encontrados = [
        coluna
        for coluna, nome in mapa.items()
        if normalizar(nome) in alvos
    ]

    if len(encontrados) == 1:
        return encontrados[0]

    return None


def mostrar_2023(df):
    origem, mapa = mapa_cabecalho_2023(
        df,
        2023,
    )

    print("CABEÇALHO TÉCNICO 2023")
    print("-" * 120)
    print(
        f"Linha de origem usada como cabeçalho: {origem}"
    )

    grupos = {
        "UF": [
            r"(^|_)uf($|_)",
            r"sigla.*uf",
            r"co.*uf",
            r"id.*uf",
        ],
        "SÉRIE/ETAPA": [
            r"serie",
            r"etapa",
        ],
        "REDE/PÚBLICA": [
            r"in.*public",
            r"rede",
            r"depend",
        ],
        "LOCALIZAÇÃO": [
            r"localiz",
        ],
        "PARTICIPANTES/PRESENTES": [
            r"particip",
            r"present",
        ],
        "MÉDIAS/PROFICIÊNCIAS": [
            r"media.*lp",
            r"media.*mt",
            r"profic.*lp",
            r"profic.*mt",
            r"proficiencia",
        ],
    }

    encontrados_grupos = {}

    for titulo, padroes in grupos.items():
        encontrados = procurar_no_mapa(
            mapa,
            padroes,
        )
        encontrados_grupos[titulo] = encontrados

        print(f"{titulo}:")
        if not encontrados:
            print("  <não localizado>")
        else:
            for coluna, nome in encontrados:
                print(
                    f"  {coluna}: {nome}"
                )

    print()
    print("FREQUÊNCIAS 2023")
    print("-" * 120)

    candidatos_exatos = {
        "IN_PUBLICA": [
            "IN_PUBLICA",
        ],
        "LOCALIZAÇÃO": [
            "ID_LOCALIZACAO",
            "CO_LOCALIZACAO",
            "TP_LOCALIZACAO",
        ],
        "SÉRIE": [
            "ID_SERIE",
            "CO_SERIE",
            "TP_SERIE",
        ],
        "UF": [
            "SIGLA_UF",
            "SG_UF",
            "ID_UF",
            "CO_UF",
        ],
    }

    for titulo, nomes in candidatos_exatos.items():
        coluna = coluna_exata(
            mapa,
            nomes,
        )

        if coluna is None:
            print(
                f"{titulo}: <coluna exata não localizada de forma única>"
            )
            continue

        print(
            f"{titulo}: {coluna} = {mapa[coluna]}"
        )
        imprimir_frequencia(
            "  valores",
            df.loc[
                df["_linha_origem"] > origem,
                coluna,
            ],
            limite=40,
        )

    print()
    print(
        "A auditoria de 2023 deve ser usada para definir a agregação "
        "ESCOLA → UF somente depois de confirmar as variáveis de "
        "participantes/presentes e as médias por etapa/disciplina."
    )
    print()


def auditar_ano(ano, caminho):
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

    origem_cabecalho = cabecalho_origem(
        df,
        ano,
    )

    granularidades = (
        df["_granularidade_origem"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
        if "_granularidade_origem" in df.columns
        else []
    )

    print("=" * 120)
    print(f"SAEB — {ano}")
    print("=" * 120)
    print(f"Arquivo Bronze: {caminho.name}")
    print(f"Linhas Bronze: {len(df):,}")
    print(f"Colunas fonte: {len(cols)}")
    print(
        f"Granularidade de origem: {granularidades}"
    )
    print(
        f"_indice_cabecalho_origem: {origem_cabecalho - 1}"
    )
    print(
        f"Linha física inicial do cabeçalho: _linha_origem={origem_cabecalho}"
    )
    print()

    print("CABEÇALHO/ESTRUTURA DE ORIGEM")
    print("-" * 120)

    for numero in range(
        origem_cabecalho,
        origem_cabecalho + 3,
    ):
        print(
            f"_linha_origem={numero}: "
            f"{formatar_linha(linha_por_origem(df, numero), cols)}"
        )

    print()

    if ano in ESTRUTURA:
        mostrar_estrutura_conhecida(
            df,
            ano,
        )
    else:
        mostrar_2023(
            df
        )


def main():
    print("=" * 120)
    print(
        "AUDITORIA PARA A CAMADA SILVER — SAEB — V2"
    )
    print("=" * 120)
    print()
    print(
        "Correção metodológica: a linha de cabeçalho não é mais "
        "inferida por uma heurística de texto."
    )
    print(
        "A auditoria usa _indice_cabecalho_origem, gravado na Bronze, "
        "como referência autoritativa da posição do cabeçalho da fonte."
    )
    print(
        "Isso evita classificar linhas de dados como cabeçalho em "
        "edições como 2015, 2017, 2019 e 2021."
    )
    print()
    print(
        "Objetivo: confirmar rede pública, localização, etapas, "
        "proficiências e, em 2023, as variáveis necessárias à "
        "agregação escola → UF."
    )
    print(
        "Nenhum arquivo Bronze ou Silver é alterado."
    )
    print()

    for ano, caminho in ARQUIVOS.items():
        auditar_ano(
            ano=ano,
            caminho=caminho,
        )

    print("=" * 120)
    print("AUDITORIA CONCLUÍDA.")
    print("Nenhum arquivo Bronze ou Silver foi alterado.")
    print("=" * 120)


if __name__ == "__main__":
    main()
