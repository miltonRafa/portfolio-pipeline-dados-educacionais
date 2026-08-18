from pathlib import Path
import pandas as pd
import re
import unicodedata


PASTA = Path("data/raw/tdi")


def normalizar(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()

    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

    texto = re.sub(r"[^a-z0-9]+", " ", texto)

    return " ".join(texto.split())


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
    key=lambda arquivo: int(
        re.search(r"20\d{2}", arquivo.name).group()
    )
)


for arquivo in arquivos:

    ano_esperado = int(
        re.search(r"20\d{2}", arquivo.name).group()
    )

    print("\n" + "=" * 110)
    print(f"ANO: {ano_esperado}")
    print(f"ARQUIVO: {arquivo.name}")
    print("=" * 110)

    excel = pd.ExcelFile(arquivo)

    # Ignorar abas vazias como Plan2 / Plan3
    aba_escolhida = None
    df = None

    for aba in excel.sheet_names:

        teste = pd.read_excel(
            arquivo,
            sheet_name=aba,
            header=None
        )

        if not teste.dropna(how="all").empty:
            aba_escolhida = aba
            df = teste
            break

    if df is None:
        print("ERRO: nenhuma aba com dados.")
        continue

    print(f"\nABA: {aba_escolhida}")

    # =========================================================
    # 1. LOCALIZAR LINHA DAS DIMENSÕES
    # =========================================================

    linha_dimensoes = None

    for i in range(min(15, len(df))):

        valores = [
            normalizar(v)
            for v in df.iloc[i].tolist()
        ]

        tem_ano = "ano" in valores

        tem_localizacao = any(
            v == "localizacao"
            for v in valores
        )

        tem_rede = any(
            v == "rede"
            or "dependencia administrativa" in v
            for v in valores
        )

        if tem_ano and tem_localizacao and tem_rede:
            linha_dimensoes = i
            break

    if linha_dimensoes is None:
        print("ERRO: linha das dimensões não encontrada.")
        continue

    dimensoes = [
        normalizar(v)
        for v in df.iloc[linha_dimensoes].tolist()
    ]

    coluna_ano = None
    coluna_geo = None
    coluna_localizacao = None
    coluna_rede = None

    for indice, nome in enumerate(dimensoes):

        if nome == "ano":
            coluna_ano = indice

        elif nome in {
            "uf",
            "sigla da uf",
        }:
            coluna_geo = indice

        elif "unidade geografica" in nome:
            coluna_geo = indice

        elif nome == "localizacao":
            coluna_localizacao = indice

        elif nome == "rede":
            coluna_rede = indice

        elif "dependencia administrativa" in nome:
            coluna_rede = indice

    if None in [
        coluna_ano,
        coluna_geo,
        coluna_localizacao,
        coluna_rede
    ]:
        print("ERRO: dimensão obrigatória não localizada.")
        print(
            coluna_ano,
            coluna_geo,
            coluna_localizacao,
            coluna_rede
        )
        continue

    # =========================================================
    # 2. VALIDAR ANO INTERNO
    # =========================================================

    serie_ano = pd.to_numeric(
        df.iloc[:, coluna_ano],
        errors="coerce"
    )

    anos_internos = sorted(
        {
            int(x)
            for x in serie_ano.dropna()
            if 2000 <= x <= 2100
        }
    )

    print(f"ANOS INTERNOS: {anos_internos}")

    if anos_internos == [ano_esperado]:
        print("VALIDAÇÃO DO ANO: OK")
    else:
        print("ATENÇÃO: ano interno divergente")

    # =========================================================
    # 3. LOCALIZAR COLUNAS AI E AF
    # =========================================================

    coluna_ai = None
    coluna_af = None

    # Procurar nas linhas de cabeçalho
    for i in range(
        linha_dimensoes,
        min(linha_dimensoes + 5, len(df))
    ):

        for indice, valor in enumerate(
            df.iloc[i].tolist()
        ):

            texto = normalizar(valor)

            if (
                "anos iniciais" in texto
                or "1 ao 5 ano" in texto
                or "1 ao 5" in texto
            ):
                coluna_ai = indice

            if (
                "anos finais" in texto
                or "6 ao 9 ano" in texto
                or "6 ao 9" in texto
            ):
                coluna_af = indice

    # Em alguns arquivos antigos aparece:
    # 1ª a 4ª Série / 1º ao 5º Ano
    # 5ª a 8ª Série / 6º ao 9º Ano
    # A busca acima prioriza a linha moderna.

    if coluna_ai is None or coluna_af is None:
        print("ERRO: AI ou AF não localizados.")
        print(
            f"AI={coluna_ai} | AF={coluna_af}"
        )
        continue

    print(
        f"COLUNAS: "
        f"ano={coluna_ano}, "
        f"geo={coluna_geo}, "
        f"localização={coluna_localizacao}, "
        f"rede={coluna_rede}, "
        f"AI={coluna_ai}, "
        f"AF={coluna_af}"
    )

    # =========================================================
    # 4. FILTRAR APENAS ANO ESPERADO
    # =========================================================

    dados = df[
        serie_ano == ano_esperado
    ].copy()

    # =========================================================
    # 5. RECONHECER AS 27 UFs
    # =========================================================

    dados["_UF"] = (
        dados.iloc[:, coluna_geo]
        .apply(normalizar)
        .map(mapa_uf)
    )

    dados_uf = dados[
        dados["_UF"].notna()
    ].copy()

    print(
        f"\nUFs reconhecidas: "
        f"{dados_uf['_UF'].nunique()} / 27"
    )

    faltantes = sorted(
        set(ufs.values())
        -
        set(dados_uf["_UF"].unique())
    )

    print(
        "UFs faltantes:",
        faltantes if faltantes else "nenhuma"
    )

    # =========================================================
    # 6. CATEGORIAS EXISTENTES
    # =========================================================

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

    # =========================================================
    # 7. FILTRAR PÚBLICA + TOTAL
    # =========================================================

    local_norm = (
        dados_uf.iloc[:, coluna_localizacao]
        .apply(normalizar)
    )

    rede_norm = (
        dados_uf.iloc[:, coluna_rede]
        .apply(normalizar)
    )

    publica = dados_uf[
        (local_norm == "total")
        &
        (rede_norm.isin(["publico", "publica"]))
    ].copy()

    print(
        f"\nPÚBLICA + LOCALIZAÇÃO TOTAL: "
        f"{publica['_UF'].nunique()} / 27"
    )

    faltantes_publica = sorted(
        set(ufs.values())
        -
        set(publica["_UF"].unique())
    )

    print(
        "UFs sem agregado público:",
        faltantes_publica
        if faltantes_publica
        else "nenhuma"
    )

    # =========================================================
    # 8. DUPLICIDADES
    # =========================================================

    contagem = publica["_UF"].value_counts()

    duplicadas = contagem[
        contagem > 1
    ]

    if len(duplicadas):
        print("\nATENÇÃO — DUPLICIDADES:")
        print(duplicadas)
    else:
        print("\nDUPLICIDADES: nenhuma")

    # =========================================================
    # 9. COBERTURA AI / AF
    # =========================================================

    valores_ai = (
        publica.iloc[:, coluna_ai]
        .replace(
            {
                "--": pd.NA,
                "-": pd.NA,
                "": pd.NA
            }
        )
    )

    valores_af = (
        publica.iloc[:, coluna_af]
        .replace(
            {
                "--": pd.NA,
                "-": pd.NA,
                "": pd.NA
            }
        )
    )

    valores_ai = pd.to_numeric(
        valores_ai,
        errors="coerce"
    )

    valores_af = pd.to_numeric(
        valores_af,
        errors="coerce"
    )

    print("\nCOBERTURA:")

    print(
        f"Anos Iniciais: "
        f"{valores_ai.notna().sum()} válidos | "
        f"{valores_ai.isna().sum()} ausentes"
    )

    print(
        f"Anos Finais:   "
        f"{valores_af.notna().sum()} válidos | "
        f"{valores_af.isna().sum()} ausentes"
    )

    if valores_ai.isna().any():

        print(
            "UFs sem AI:",
            publica.loc[
                valores_ai.isna(),
                "_UF"
            ].tolist()
        )

    if valores_af.isna().any():

        print(
            "UFs sem AF:",
            publica.loc[
                valores_af.isna(),
                "_UF"
            ].tolist()
        )

    # =========================================================
    # 10. FAIXA DOS VALORES
    # =========================================================

    if valores_ai.notna().any():
        print(
            f"\nAI mínimo/máximo: "
            f"{valores_ai.min()} / "
            f"{valores_ai.max()}"
        )

    if valores_af.notna().any():
        print(
            f"AF mínimo/máximo: "
            f"{valores_af.min()} / "
            f"{valores_af.max()}"
        )