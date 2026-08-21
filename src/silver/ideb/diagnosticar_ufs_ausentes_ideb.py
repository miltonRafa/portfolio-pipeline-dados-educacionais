from pathlib import Path
import unicodedata

import pandas as pd


BRONZE_DIR = Path("data/bronze/ideb")

ARQUIVOS = {
    "ANOS_INICIAIS": BRONZE_DIR / "ideb_ai.parquet",
    "ANOS_FINAIS": BRONZE_DIR / "ideb_af.parquet",
}

UF_ESPERADAS = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba", "Pernambuco",
    "Alagoas", "Sergipe", "Bahia", "Minas Gerais", "Espírito Santo",
    "Rio de Janeiro", "São Paulo", "Paraná", "Santa Catarina",
    "Rio Grande do Sul", "Mato Grosso do Sul", "Mato Grosso", "Goiás",
    "Distrito Federal",
]

ALVOS = {
    "RN": "rio grande do norte",
    "RS": "rio grande do sul",
    "MS": "mato grosso do sul",
}


def normalizar(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return " ".join(texto.casefold().split())


def linha_tecnica(df):
    indices = (
        df["_indice_cabecalho_origem"]
        .dropna()
        .unique()
    )

    if len(indices) != 1:
        raise RuntimeError(
            f"_indice_cabecalho_origem não é único: {indices.tolist()}"
        )

    linha_origem = int(indices[0]) + 1
    linha = df[df["_linha_origem"] == linha_origem]
    if len(linha) != 1:
        raise RuntimeError(
            f"Linha técnica _linha_origem={linha_origem} "
            "não encontrada de forma única."
        )
    return linha.iloc[0]


def colunas_ideb(df):
    tecnica = linha_tecnica(df)
    resultado = {}

    for ano in [2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023]:
        alvo = f"VL_OBSERVADO_{ano}"
        encontradas = [
            c for c in df.columns
            if str(c).startswith("col_")
            and str(tecnica[c]).strip() == alvo
        ]
        if len(encontradas) != 1:
            raise RuntimeError(f"{alvo}: {encontradas}")
        resultado[ano] = encontradas[0]

    return resultado


def eh_linha_de_dados(linha):
    rede = normalizar(linha["col_002"])
    redes = {
        "total",
        "publica",
        "privada",
        "estadual",
        "total (3)(4)",
        "publica (4)",
        "privada (2)",
        "total (4)",
    }
    return rede in redes


def auditar(etapa, caminho):
    df = pd.read_parquet(caminho)
    ideb = colunas_ideb(df)

    print("=" * 120)
    print(f"DIAGNÓSTICO IDEB — {etapa}")
    print("=" * 120)

    dados = df[
        df.apply(eh_linha_de_dados, axis=1)
    ].copy()

    print(f"Linhas de dados reconhecidas por rótulo de rede: {len(dados)}")
    print()

    print("SEQUÊNCIA COMPLETA DE GEOGRAFIAS E REDES NA BRONZE")
    print("-" * 120)

    for _, linha in dados.iterrows():
        geo = linha["col_001"]
        rede = linha["col_002"]
        origem = int(linha["_linha_origem"])

        print(
            f"_linha_origem={origem:>3} | "
            f"geografia={geo!r} | "
            f"rede={rede!r}"
        )

    print()
    print("GEOGRAFIAS ÚNICAS NA ORDEM EM QUE APARECEM")
    print("-" * 120)

    unicas = []
    for valor in dados["col_001"]:
        bruto = "" if pd.isna(valor) else str(valor).strip()
        if bruto and bruto not in unicas:
            unicas.append(bruto)

    for i, geo in enumerate(unicas, start=1):
        print(f"{i:>2}. {geo!r}")

    print()
    print("BUSCA LITERAL/NORMALIZADA DOS TRÊS ALVOS")
    print("-" * 120)

    for sigla, nome in ALVOS.items():
        matches = []

        for _, linha in df.iterrows():
            bruto = linha["col_001"]
            norm = normalizar(bruto)

            if nome in norm:
                matches.append(linha)

        if not matches:
            print(f"{sigla}: nenhum valor em col_001 contém {nome!r}.")
        else:
            for linha in matches:
                print(
                    f"{sigla}: _linha_origem={int(linha['_linha_origem'])} | "
                    f"col_001={linha['col_001']!r} | "
                    f"col_002={linha['col_002']!r}"
                )

    print()
    print("VIZINHANÇA DOS PONTOS ONDE AS UFs DEVERIAM APARECER")
    print("-" * 120)

    # Mostra blocos próximos às UFs que vêm antes/depois na ordem oficial.
    vizinhos = {
        "RN": {"antes": "ceara", "depois": "paraiba"},
        "RS": {"antes": "santa catarina", "depois": "mato grosso do sul"},
        "MS": {"antes": "rio grande do sul", "depois": "mato grosso"},
    }

    for sigla, refs in vizinhos.items():
        print(f"\n{sigla}:")

        indices = []
        for idx, linha in dados.iterrows():
            geo = normalizar(linha["col_001"])
            if geo in {refs["antes"], refs["depois"]}:
                indices.append(idx)

        if not indices:
            print("  Não foi possível localizar vizinhos suficientes.")
            continue

        inicio = max(min(indices) - 3, df.index.min())
        fim = min(max(indices) + 3, df.index.max())

        trecho = df.loc[inicio:fim]

        for _, linha in trecho.iterrows():
            origem = linha["_linha_origem"]
            geo = linha["col_001"]
            rede = linha["col_002"]

            if pd.isna(origem):
                continue

            valores = " | ".join(
                f"{ano}={linha[coluna]!r}"
                for ano, coluna in ideb.items()
            )

            print(
                f"  _linha_origem={int(origem):>3} | "
                f"geo={geo!r} | rede={rede!r} | {valores}"
            )

    print()


def main():
    print("=" * 120)
    print("DIAGNÓSTICO DAS UFs AUSENTES NA BRONZE DO IDEB")
    print("=" * 120)
    print()
    print(
        "Objetivo: verificar se RN, RS e MS estão realmente ausentes da Bronze "
        "ou se aparecem com outra grafia/posição."
    )
    print(
        "Nenhum arquivo é alterado."
    )
    print()

    for etapa, caminho in ARQUIVOS.items():
        if not caminho.exists():
            raise FileNotFoundError(caminho)
        auditar(etapa, caminho)

    print("=" * 120)
    print("DIAGNÓSTICO CONCLUÍDO.")
    print("=" * 120)


if __name__ == "__main__":
    main()
