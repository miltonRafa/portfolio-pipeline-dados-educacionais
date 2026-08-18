from pathlib import Path
import pandas as pd
import re
import unicodedata


PASTA = Path("data/raw/rendimento")


def normalizar(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()

    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

    return texto


ufs = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}


# Permite reconhecer tanto siglas quanto nomes completos
mapa_uf = {}

for sigla, nome in ufs.items():
    mapa_uf[normalizar(sigla)] = nome
    mapa_uf[normalizar(nome)] = nome


arquivos = sorted(
    [
        arquivo
        for arquivo in PASTA.iterdir()
        if arquivo.suffix.lower() in {".xls", ".xlsx"}
    ],
    key=lambda p: int(re.search(r"20\d{2}", p.name).group())
)


for arquivo in arquivos:

    ano = int(re.search(r"20\d{2}", arquivo.name).group())

    print("\n" + "=" * 110)
    print(f"ANO: {ano}")
    print(f"ARQUIVO: {arquivo.name}")
    print("=" * 110)

    excel = pd.ExcelFile(arquivo)
    aba = excel.sheet_names[0]

    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None
    )

    # ---------------------------------------------------------
    # Encontrar linha que contém os nomes das dimensões
    # ---------------------------------------------------------

    linha_cabecalho = None

    for i in range(min(15, len(df))):
        valores = [normalizar(v) for v in df.iloc[i].tolist()]

        if "ano" in valores:
            linha_cabecalho = i
            break

    if linha_cabecalho is None:
        print("ERRO: linha de cabeçalho não localizada.")
        continue

    cabecalho = [
        normalizar(v)
        for v in df.iloc[linha_cabecalho].tolist()
    ]

    # ---------------------------------------------------------
    # Localizar colunas
    # ---------------------------------------------------------

    coluna_ano = None
    coluna_geo = None
    coluna_localizacao = None
    coluna_rede = None

    for indice, nome in enumerate(cabecalho):

        if nome == "ano":
            coluna_ano = indice

        elif nome == "uf":
            coluna_geo = indice

        elif "unidade geografica" in nome:
            coluna_geo = indice

        elif nome == "localizacao":
            coluna_localizacao = indice

        elif nome == "rede":
            coluna_rede = indice

        elif "dependencia administrativa" in nome:
            coluna_rede = indice

    print(f"\nABA: {aba}")
    print(f"LINHA DO CABEÇALHO: {linha_cabecalho}")

    print(
        "COLUNAS IDENTIFICADAS:",
        f"ano={coluna_ano},",
        f"geografia={coluna_geo},",
        f"localização={coluna_localizacao},",
        f"rede={coluna_rede}"
    )

    if None in [
        coluna_ano,
        coluna_geo,
        coluna_localizacao,
        coluna_rede
    ]:
        print("ERRO: alguma dimensão não foi encontrada.")
        continue

    # ---------------------------------------------------------
    # Manter somente linhas de dados do ano
    # ---------------------------------------------------------

    anos_lidos = pd.to_numeric(
        df.iloc[:, coluna_ano],
        errors="coerce"
    )

    dados = df[anos_lidos == ano].copy()

    # ---------------------------------------------------------
    # Reconhecer somente as 27 UFs
    # ---------------------------------------------------------

    dados["_geo_norm"] = (
        dados.iloc[:, coluna_geo]
        .apply(normalizar)
    )

    dados["_UF"] = dados["_geo_norm"].map(mapa_uf)

    dados_uf = dados[dados["_UF"].notna()].copy()

    print(
        f"\nUFs reconhecidas: "
        f"{dados_uf['_UF'].nunique()} / 27"
    )

    faltantes = sorted(
        set(ufs.values()) -
        set(dados_uf["_UF"].unique())
    )

    print(
        "UFs faltantes:",
        faltantes if faltantes else "nenhuma"
    )

    # ---------------------------------------------------------
    # Categorias originais
    # ---------------------------------------------------------

    localizacoes = sorted(
        dados_uf.iloc[:, coluna_localizacao]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    redes = sorted(
        dados_uf.iloc[:, coluna_rede]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    print("\nLOCALIZAÇÕES:")
    print(localizacoes)

    print("\nREDES / DEPENDÊNCIAS:")
    print(redes)

    # ---------------------------------------------------------
    # Verificar linha pública + localização total
    # ---------------------------------------------------------

    local_norm = (
        dados_uf.iloc[:, coluna_localizacao]
        .apply(normalizar)
    )

    rede_norm = (
        dados_uf.iloc[:, coluna_rede]
        .apply(normalizar)
    )

    mascara_publica_total = (
        (local_norm == "total")
        &
        (rede_norm.isin(["publico", "publica"]))
    )

    publica_total = dados_uf[
        mascara_publica_total
    ].copy()

    quantidade = publica_total["_UF"].nunique()

    print("\nREDE PÚBLICA + LOCALIZAÇÃO TOTAL:")
    print(f"{quantidade} / 27 UFs")

    faltantes_publica = sorted(
        set(ufs.values()) -
        set(publica_total["_UF"].unique())
    )

    print(
        "UFs sem agregado público total:",
        faltantes_publica
        if faltantes_publica
        else "nenhuma"
    )

    # ---------------------------------------------------------
    # Verificar duplicidade
    # ---------------------------------------------------------

    duplicadas = (
        publica_total["_UF"]
        .value_counts()
    )

    duplicadas = duplicadas[
        duplicadas > 1
    ]

    if len(duplicadas):
        print("\nATENÇÃO — duplicidades:")
        print(duplicadas)
    else:
        print("\nDuplicidades: nenhuma")