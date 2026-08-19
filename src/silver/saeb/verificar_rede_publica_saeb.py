from pathlib import Path
import math
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

UF_CODIGO_SIGLA = {
    11: "RO",
    12: "AC",
    13: "AM",
    14: "RR",
    15: "PA",
    16: "AP",
    17: "TO",
    21: "MA",
    22: "PI",
    23: "CE",
    24: "RN",
    25: "PB",
    26: "PE",
    27: "AL",
    28: "SE",
    29: "BA",
    31: "MG",
    32: "ES",
    33: "RJ",
    35: "SP",
    41: "PR",
    42: "SC",
    43: "RS",
    50: "MS",
    51: "MT",
    52: "GO",
    53: "DF",
}

UF_NOME_SIGLA = {
    "rondonia": "RO",
    "acre": "AC",
    "amazonas": "AM",
    "roraima": "RR",
    "para": "PA",
    "amapa": "AP",
    "tocantins": "TO",
    "maranhao": "MA",
    "piaui": "PI",
    "ceara": "CE",
    "rio grande do norte": "RN",
    "paraiba": "PB",
    "pernambuco": "PE",
    "alagoas": "AL",
    "sergipe": "SE",
    "bahia": "BA",
    "minas gerais": "MG",
    "espirito santo": "ES",
    "rio de janeiro": "RJ",
    "sao paulo": "SP",
    "parana": "PR",
    "santa catarina": "SC",
    "rio grande do sul": "RS",
    "mato grosso do sul": "MS",
    "mato grosso": "MT",
    "goias": "GO",
    "distrito federal": "DF",
}

UFS = set(UF_CODIGO_SIGLA.values())


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    return " ".join(texto.casefold().split())


def numero(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto in {"", "-", "--"}:
        return None

    texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return None


def sigla_por_nome(valor):
    return UF_NOME_SIGLA.get(
        normalizar_texto(valor)
    )


def sigla_por_codigo(valor):
    n = numero(valor)

    if n is None:
        return None

    return UF_CODIGO_SIGLA.get(
        int(n)
    )


def conferir_27_ufs(df, coluna_uf, conversor, contexto):
    trabalho = df.copy()
    trabalho["_UF"] = trabalho[
        coluna_uf
    ].map(conversor)

    ufs = set(
        trabalho["_UF"]
        .dropna()
    )

    faltantes = sorted(
        UFS - ufs
    )

    extras = sorted(
        ufs - UFS
    )

    print(
        f"{contexto}: linhas={len(trabalho):,} | "
        f"UFs={len(ufs)} | faltantes={faltantes} | extras={extras}"
    )

    return trabalho


def relatorio_metricas(df, colunas):
    for nome, coluna in colunas.items():
        valores = df[
            coluna
        ].map(numero)

        ausentes = int(
            valores.isna().sum()
        )

        zeros = int(
            (valores == 0).sum()
        )

        validos = valores.dropna()

        minimo = (
            validos.min()
            if not validos.empty
            else None
        )

        maximo = (
            validos.max()
            if not validos.empty
            else None
        )

        print(
            f"  {nome}: "
            f"ausentes={ausentes} | "
            f"zeros={zeros} | "
            f"mín={minimo} | "
            f"máx={maximo}"
        )


def verificar_2007_2009(ano, df):
    print("=" * 120)
    print(
        f"SAEB {ano} — agregado público disponível na fonte"
    )
    print("=" * 120)

    redes = sorted(
        {
            str(v).strip()
            for v in df["col_004"].dropna()
            if str(v).strip()
        }
    )

    print(
        "Categorias de rede: "
        + " | ".join(redes)
    )

    federal_explicita = any(
        normalizar_texto(v) == "federal"
        for v in redes
    )

    print(
        f"Categoria Federal isolada presente: {federal_explicita}"
    )

    alvo = df[
        (df["col_004"].astype(str).str.strip() == "Total - Estadual e Municipal")
        & (df["col_005"].astype(str).str.strip() == "Total")
        & (df["col_006"].astype(str).str.strip() == "Total")
    ].copy()

    alvo = conferir_27_ufs(
        alvo,
        "col_003",
        sigla_por_nome,
        "Total - Estadual e Municipal / localização Total / capital Total",
    )

    duplicadas = int(
        alvo["_UF"].duplicated().sum()
    )

    print(
        f"Duplicidades por UF: {duplicadas}"
    )

    relatorio_metricas(
        alvo,
        {
            "AI_LP": "col_007",
            "AI_MT": "col_008",
            "AF_LP": "col_009",
            "AF_MT": "col_010",
        },
    )

    print()


def verificar_2011(df):
    print("=" * 120)
    print(
        "SAEB 2011 — código público e estrato total"
    )
    print("=" * 120)

    print(
        "Regra já definida no projeto: ID_TIPO_REDE=5 representa rede pública."
    )
    print(
        "Nesta verificação conferimos cardinalidade e completude com "
        "ID_LOCALIZACAO=0 e ID_CAPITAL=0."
    )

    for serie, etapa in [
        ("5", "ANOS_INICIAIS"),
        ("9", "ANOS_FINAIS"),
    ]:
        alvo = df[
            (df["col_005"].astype(str).str.strip() == serie)
            & (df["col_006"].astype(str).str.strip() == "5")
            & (df["col_007"].astype(str).str.strip() == "0")
            & (df["col_008"].astype(str).str.strip() == "0")
        ].copy()

        alvo = conferir_27_ufs(
            alvo,
            "col_003",
            lambda v: str(v).strip() if str(v).strip() in UFS else None,
            etapa,
        )

        print(
            f"  duplicidades por UF: "
            f"{int(alvo['_UF'].duplicated().sum())}"
        )

        relatorio_metricas(
            alvo,
            {
                "NU_PARTICIPANTES": "col_009",
                "LP": "col_010",
                "MT": "col_011",
            },
        )

    print()


def verificar_2013_2021(ano, df):
    print("=" * 120)
    print(
        f"SAEB {ano} — agregado público oficial da UF"
    )
    print("=" * 120)

    if ano in {2013, 2015}:
        uf = "col_001"
        rede = "col_002"
        loc = "col_003"
        cap = "col_004"
        metricas = {
            "AI_LP": "col_005",
            "AI_MT": "col_006",
            "AF_LP": "col_007",
            "AF_MT": "col_008",
        }
    elif ano == 2017:
        uf = "col_002"
        rede = "col_003"
        loc = "col_004"
        cap = "col_005"
        metricas = {
            "AI_LP": "col_006",
            "AI_MT": "col_007",
            "AF_LP": "col_008",
            "AF_MT": "col_009",
        }
    else:
        uf = "col_002"
        rede = "col_003"
        loc = "col_004"
        cap = "col_005"
        metricas = {
            "AI_LP": "col_008",
            "AI_MT": "col_009",
            "AF_LP": "col_010",
            "AF_MT": "col_011",
        }

    alvo = df[
        (df[rede].astype(str).str.strip() == "Total - Federal, Estadual e Municipal")
        & (df[loc].astype(str).str.strip() == "Total")
        & (df[cap].astype(str).str.strip() == "Total")
    ].copy()

    alvo = conferir_27_ufs(
        alvo,
        uf,
        sigla_por_nome,
        "Total - Federal, Estadual e Municipal / localização Total / capital Total",
    )

    print(
        f"Duplicidades por UF: "
        f"{int(alvo['_UF'].duplicated().sum())}"
    )

    relatorio_metricas(
        alvo,
        metricas,
    )

    if ano == 2015:
        print(
            "  Observação 2015: a fonte informa que valor 0 significa "
            "que não foi possível calcular a média para o estrato."
        )

    print()


def media_ponderada(grupo, coluna_media, coluna_peso):
    medias = grupo[
        coluna_media
    ].map(numero)

    pesos = grupo[
        coluna_peso
    ].map(numero)

    mascara = (
        medias.notna()
        & pesos.notna()
        & (pesos > 0)
    )

    medias = medias[
        mascara
    ]

    pesos = pesos[
        mascara
    ]

    if medias.empty:
        return None, 0, 0

    valor = (
        (medias * pesos).sum()
        / pesos.sum()
    )

    return (
        float(valor),
        int(mascara.sum()),
        float(pesos.sum()),
    )


def verificar_2023(df):
    print("=" * 120)
    print(
        "SAEB 2023 — diagnóstico da agregação ESCOLA → UF"
    )
    print("=" * 120)

    dados = df[
        df["_linha_origem"] > 1
    ].copy()

    contagem_publica = (
        dados["col_007"]
        .astype(str)
        .str.strip()
        .value_counts()
        .to_dict()
    )

    print(
        f"IN_PUBLICA na Bronze 2023: {contagem_publica}"
    )

    publicas = dados[
        dados["col_007"]
        .astype(str)
        .str.strip()
        == "1"
    ].copy()

    publicas["_UF"] = (
        publicas["col_003"]
        .map(sigla_por_codigo)
    )

    print(
        f"Linhas de escolas públicas: {len(publicas):,}"
    )
    print(
        f"UFs reconhecidas: {publicas['_UF'].nunique()}/27"
    )

    faltantes = sorted(
        UFS - set(publicas["_UF"].dropna())
    )

    print(
        f"UFs faltantes: {faltantes}"
    )

    configuracoes = {
        "ANOS_INICIAIS": {
            "PESO": "col_014",
            "LP": "col_128",
            "MT": "col_129",
        },
        "ANOS_FINAIS": {
            "PESO": "col_038",
            "LP": "col_130",
            "MT": "col_131",
        },
    }

    print()
    print(
        "CANDIDATO DE AGREGAÇÃO: média das médias escolares "
        "ponderada por NU_PRESENTES da etapa."
    )
    print(
        "A saída abaixo é diagnóstica; ela ainda não autoriza a transformação."
    )

    for etapa, cfg in configuracoes.items():
        print()
        print(etapa)
        print("-" * 120)

        sem_peso = int(
            publicas[cfg["PESO"]]
            .map(numero)
            .isna()
            .sum()
        )

        print(
            f"Escolas sem NU_PRESENTES da etapa: {sem_peso:,}"
        )

        resultados = []

        for uf, grupo in publicas.groupby("_UF"):
            if not uf:
                continue

            lp, n_lp, peso_lp = media_ponderada(
                grupo,
                cfg["LP"],
                cfg["PESO"],
            )

            mt, n_mt, peso_mt = media_ponderada(
                grupo,
                cfg["MT"],
                cfg["PESO"],
            )

            resultados.append(
                {
                    "UF": uf,
                    "LP": lp,
                    "MT": mt,
                    "ESCOLAS_LP": n_lp,
                    "ESCOLAS_MT": n_mt,
                    "PRESENTES_LP": peso_lp,
                    "PRESENTES_MT": peso_mt,
                }
            )

        resultado = pd.DataFrame(
            resultados
        ).sort_values("UF")

        print(
            f"UFs agregadas: {len(resultado)}/27"
        )

        faltantes_resultado = sorted(
            UFS - set(resultado["UF"])
        )

        print(
            f"UFs sem resultado agregado: {faltantes_resultado}"
        )

        print(
            f"Valores LP ausentes após agregação: "
            f"{int(resultado['LP'].isna().sum())}"
        )
        print(
            f"Valores MT ausentes após agregação: "
            f"{int(resultado['MT'].isna().sum())}"
        )

        print(
            "Amostra das médias ponderadas:"
        )

        for linha in resultado.head(10).itertuples(index=False):
            print(
                f"  {linha.UF}: "
                f"LP={linha.LP:.4f} | "
                f"MT={linha.MT:.4f} | "
                f"escolas_lp={linha.ESCOLAS_LP} | "
                f"presentes_lp={linha.PRESENTES_LP:.0f}"
            )

    print()
    print(
        "IMPORTANTE: a média ponderada por presentes só deve ser adotada "
        "como regra Silver depois de validada contra uma referência oficial "
        "de agregação UF ou contra documentação metodológica suficiente."
    )
    print()


def main():
    print("=" * 120)
    print(
        "VERIFICAÇÃO FOCADA — REDE PÚBLICA E AGREGAÇÃO DO SAEB"
    )
    print("=" * 120)
    print()
    print(
        "Objetivo: fechar as regras de seleção da população pública em 2007–2021 "
        "e produzir um diagnóstico, ainda não definitivo, da agregação 2023."
    )
    print(
        "Nenhum arquivo Bronze ou Silver é alterado."
    )
    print()

    for ano in [2007, 2009]:
        verificar_2007_2009(
            ano,
            pd.read_parquet(ARQUIVOS[ano]),
        )

    verificar_2011(
        pd.read_parquet(ARQUIVOS[2011])
    )

    for ano in [2013, 2015, 2017, 2019, 2021]:
        verificar_2013_2021(
            ano,
            pd.read_parquet(ARQUIVOS[ano]),
        )

    verificar_2023(
        pd.read_parquet(ARQUIVOS[2023])
    )

    print("=" * 120)
    print("VERIFICAÇÃO CONCLUÍDA.")
    print("Nenhum arquivo Bronze ou Silver foi alterado.")
    print("=" * 120)


if __name__ == "__main__":
    main()
