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

    # Facilita reconhecer 1º, 1ª, hífens etc.
    texto = re.sub(r"[^a-z0-9]+", " ", texto)

    return " ".join(texto.split())


def preencher_direita(valores):
    resultado = []
    atual = ""

    for valor in valores:
        texto = normalizar(valor)

        if texto:
            atual = texto

        resultado.append(atual)

    return resultado


def identificar_medida(texto):
    if "taxa de aprovacao" in texto:
        return "APROVACAO"

    if "taxa de reprovacao" in texto:
        return "REPROVACAO"

    if "taxa de abandono" in texto:
        return "ABANDONO"

    return None


def identificar_etapa(texto):
    if (
        "anos iniciais" in texto
        or "1 a 4" in texto
        or "1 ao 5" in texto
    ):
        return "AI"

    if (
        "anos finais" in texto
        or "5 a 8" in texto
        or "6 ao 9" in texto
    ):
        return "AF"

    return None


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
    key=lambda p: int(re.search(r"20\d{2}", p.name).group())
)


for arquivo in arquivos:

    ano_esperado = int(
        re.search(r"20\d{2}", arquivo.name).group()
    )

    print("\n" + "=" * 110)
    print(f"ARQUIVO: {arquivo.name}")
    print(f"ANO ESPERADO PELA ORGANIZAÇÃO LOCAL: {ano_esperado}")
    print("=" * 110)

    excel = pd.ExcelFile(arquivo)
    aba = excel.sheet_names[0]

    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None
    )

    # =========================================================
    # 1. LOCALIZAR CABEÇALHO DAS DIMENSÕES
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
        print("ERRO: cabeçalho das dimensões não localizado.")
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

    if None in [
        coluna_ano,
        coluna_geo,
        coluna_localizacao,
        coluna_rede
    ]:
        print("ERRO: dimensão necessária não encontrada.")
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
            int(valor)
            for valor in serie_ano.dropna()
            if 2000 <= valor <= 2100
        }
    )

    print(f"\nABA: {aba}")
    print(f"ANOS ENCONTRADOS INTERNAMENTE: {anos_internos}")

    if anos_internos == [ano_esperado]:
        print("VALIDAÇÃO DO ANO: OK")
    else:
        print("ATENÇÃO: ano interno diferente do esperado")

    # =========================================================
    # 3. LOCALIZAR LINHA DOS GRUPOS
    #    APROVAÇÃO / REPROVAÇÃO / ABANDONO
    # =========================================================

    linha_medidas = None

    for i in range(linha_dimensoes + 1):

        valores = [
            normalizar(v)
            for v in df.iloc[i].tolist()
        ]

        tem_aprovacao = any(
            "taxa de aprovacao" in v
            for v in valores
        )

        tem_reprovacao = any(
            "taxa de reprovacao" in v
            for v in valores
        )

        tem_abandono = any(
            "taxa de abandono" in v
            for v in valores
        )

        if (
            tem_aprovacao
            and tem_reprovacao
            and tem_abandono
        ):
            linha_medidas = i
            break

    if linha_medidas is None:
        print("ERRO: linha das medidas não localizada.")
        continue

    grupos = preencher_direita(
        df.iloc[linha_medidas].tolist()
    )

    # =========================================================
    # 4. LOCALIZAR LINHA DAS ETAPAS
    # =========================================================

    linha_etapas = None

    for i in range(linha_dimensoes, min(linha_dimensoes + 5, len(df))):

        valores = [
            normalizar(v)
            for v in df.iloc[i].tolist()
        ]

        etapas_encontradas = [
            identificar_etapa(v)
            for v in valores
        ]

        if (
            "AI" in etapas_encontradas
            and "AF" in etapas_encontradas
        ):
            linha_etapas = i
            break

    if linha_etapas is None:
        print("ERRO: linha das etapas não localizada.")
        continue

    etapas = [
        normalizar(v)
        for v in df.iloc[linha_etapas].tolist()
    ]

    # =========================================================
    # 5. IDENTIFICAR AS SEIS COLUNAS NECESSÁRIAS
    # =========================================================

    colunas = {}

    for indice in range(df.shape[1]):

        medida = identificar_medida(
            grupos[indice]
        )

        etapa = identificar_etapa(
            etapas[indice]
        )

        if medida and etapa:
            chave = (medida, etapa)
            colunas[chave] = indice

    esperadas = [
        ("APROVACAO", "AI"),
        ("APROVACAO", "AF"),
        ("REPROVACAO", "AI"),
        ("REPROVACAO", "AF"),
        ("ABANDONO", "AI"),
        ("ABANDONO", "AF"),
    ]

    print("\nCOLUNAS IDENTIFICADAS:")

    for chave in esperadas:
        print(
            f"{chave[0]:11} {chave[1]}:",
            colunas.get(chave, "NÃO ENCONTRADA")
        )

    faltando = [
        chave
        for chave in esperadas
        if chave not in colunas
    ]

    if faltando:
        print("\nERRO: faltam colunas necessárias:")
        print(faltando)
        continue

    # =========================================================
    # 6. FILTRAR O ANO
    # =========================================================

    dados = df[
        serie_ano == ano_esperado
    ].copy()

    # =========================================================
    # 7. RECONHECER AS 27 UFs
    # =========================================================

    dados["_UF"] = (
        dados.iloc[:, coluna_geo]
        .apply(normalizar)
        .map(mapa_uf)
    )

    dados = dados[
        dados["_UF"].notna()
    ].copy()

    # =========================================================
    # 8. FILTRAR PÚBLICA + LOCALIZAÇÃO TOTAL
    # =========================================================

    localizacao = (
        dados.iloc[:, coluna_localizacao]
        .apply(normalizar)
    )

    rede = (
        dados.iloc[:, coluna_rede]
        .apply(normalizar)
    )

    publica = dados[
        (localizacao == "total")
        &
        (rede.isin(["publico", "publica"]))
    ].copy()

    print(
        f"\nREGISTROS PÚBLICA + TOTAL: "
        f"{publica['_UF'].nunique()} / 27 UFs"
    )

    # =========================================================
    # 9. VERIFICAR VALORES
    # =========================================================

    series = {}

    print("\nCOBERTURA DAS SEIS MEDIDAS:")

    for chave in esperadas:

        indice = colunas[chave]

        valores = (
            publica.iloc[:, indice]
            .replace(
                {
                    "--": pd.NA,
                    "-": pd.NA,
                    "": pd.NA,
                }
            )
        )

        valores = pd.to_numeric(
            valores,
            errors="coerce"
        )

        series[chave] = valores

        validos = valores.notna().sum()
        ausentes = valores.isna().sum()

        print(
            f"{chave[0]:11} {chave[1]}: "
            f"{validos} válidos | "
            f"{ausentes} ausentes"
        )

        if ausentes > 0:

            ufs_ausentes = publica.loc[
                valores.isna(),
                "_UF"
            ].tolist()

            print(
                "   UFs sem valor:",
                ufs_ausentes
            )

    # =========================================================
    # 10. VALIDAÇÃO:
    #     APROVAÇÃO + REPROVAÇÃO + ABANDONO ≈ 100
    # =========================================================

    print("\nVALIDAÇÃO DA SOMA:")

    for etapa in ["AI", "AF"]:

        aprovacao = series[
            ("APROVACAO", etapa)
        ]

        reprovacao = series[
            ("REPROVACAO", etapa)
        ]

        abandono = series[
            ("ABANDONO", etapa)
        ]

        soma = (
            aprovacao
            + reprovacao
            + abandono
        )

        completos = soma.notna()

        desvio = (
            soma[completos] - 100
        ).abs()

        if len(desvio) == 0:
            print(
                f"{etapa}: "
                "sem registros completos para validar"
            )
            continue

        maior_desvio = desvio.max()

        fora_tolerancia = (
            desvio > 0.2
        ).sum()

        print(
            f"{etapa}: "
            f"maior desvio = {maior_desvio:.2f} | "
            f"fora da tolerância (>0,2) = "
            f"{fora_tolerancia}"
        )

        if fora_tolerancia > 0:

            indices_problema = (
                desvio[
                    desvio > 0.2
                ].index
            )

            for idx in indices_problema:

                uf = publica.loc[idx, "_UF"]

                print(
                    f"   {uf}: "
                    f"soma = {soma.loc[idx]:.2f}"
                )