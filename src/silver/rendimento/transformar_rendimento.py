from pathlib import Path
import re
import unicodedata

import pandas as pd


BRONZE_DIR = Path("data/bronze/rendimento")
SILVER_DIR = Path("data/silver/rendimento")

ARQUIVO_SILVER = "rendimento_2007_2023.parquet"

ANOS = list(range(2007, 2024))

UFS = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}

NOMES_UF = {
    "acre": "AC",
    "alagoas": "AL",
    "amapa": "AP",
    "amazonas": "AM",
    "bahia": "BA",
    "ceara": "CE",
    "distrito federal": "DF",
    "espirito santo": "ES",
    "goias": "GO",
    "maranhao": "MA",
    "mato grosso": "MT",
    "mato grosso do sul": "MS",
    "minas gerais": "MG",
    "para": "PA",
    "paraiba": "PB",
    "parana": "PR",
    "pernambuco": "PE",
    "piaui": "PI",
    "rio de janeiro": "RJ",
    "rio grande do norte": "RN",
    "rio grande do sul": "RS",
    "rondonia": "RO",
    "roraima": "RR",
    "santa catarina": "SC",
    "sao paulo": "SP",
    "sergipe": "SE",
    "tocantins": "TO",
}

# A configuração abaixo é intencionalmente explícita.
# Ela materializa as mudanças estruturais observadas na auditoria
# da Bronze e evita inferência automática de colunas.
CONFIG = {
    2007: {
        "uf": "col_003",
        "localizacao": "col_004",
        "rede": "col_005",
        "rede_publica": "publico",
        "metricas": {
            ("ANOS_INICIAIS", "APROVACAO"): "col_015",
            ("ANOS_FINAIS", "APROVACAO"): "col_016",
            ("ANOS_INICIAIS", "REPROVACAO"): "col_033",
            ("ANOS_FINAIS", "REPROVACAO"): "col_034",
            ("ANOS_INICIAIS", "ABANDONO"): "col_051",
            ("ANOS_FINAIS", "ABANDONO"): "col_052",
        },
    },
    **{
        ano: {
            "uf": "col_002",
            "localizacao": "col_003",
            "rede": "col_004",
            "rede_publica": "publico",
            "metricas": {
                ("ANOS_INICIAIS", "APROVACAO"): "col_014",
                ("ANOS_FINAIS", "APROVACAO"): "col_015",
                ("ANOS_INICIAIS", "REPROVACAO"): "col_032",
                ("ANOS_FINAIS", "REPROVACAO"): "col_033",
                ("ANOS_INICIAIS", "ABANDONO"): "col_050",
                ("ANOS_FINAIS", "ABANDONO"): "col_051",
            },
        }
        for ano in range(2008, 2011)
    },
    **{
        ano: {
            "uf": "col_002",
            "localizacao": "col_003",
            "rede": "col_004",
            "rede_publica": "publico",
            "metricas": {
                ("ANOS_INICIAIS", "APROVACAO"): "col_006",
                ("ANOS_FINAIS", "APROVACAO"): "col_007",
                ("ANOS_INICIAIS", "REPROVACAO"): "col_024",
                ("ANOS_FINAIS", "REPROVACAO"): "col_025",
                ("ANOS_INICIAIS", "ABANDONO"): "col_042",
                ("ANOS_FINAIS", "ABANDONO"): "col_043",
            },
        }
        for ano in range(2011, 2015)
    },
    2015: {
        "uf": "col_002",
        "localizacao": "col_003",
        "rede": "col_004",
        "rede_publica": "publica",
        "metricas": {
            ("ANOS_INICIAIS", "APROVACAO"): "col_006",
            ("ANOS_FINAIS", "APROVACAO"): "col_007",
            ("ANOS_INICIAIS", "REPROVACAO"): "col_024",
            ("ANOS_FINAIS", "REPROVACAO"): "col_025",
            ("ANOS_INICIAIS", "ABANDONO"): "col_042",
            ("ANOS_FINAIS", "ABANDONO"): "col_043",
        },
    },
    2016: {
        "uf": "col_003",
        "localizacao": "col_004",
        "rede": "col_005",
        "rede_publica": "publica",
        "metricas": {
            ("ANOS_INICIAIS", "APROVACAO"): "col_007",
            ("ANOS_FINAIS", "APROVACAO"): "col_008",
            ("ANOS_INICIAIS", "REPROVACAO"): "col_025",
            ("ANOS_FINAIS", "REPROVACAO"): "col_026",
            ("ANOS_INICIAIS", "ABANDONO"): "col_043",
            ("ANOS_FINAIS", "ABANDONO"): "col_044",
        },
    },
    **{
        ano: {
            "uf": "col_002",
            "localizacao": "col_003",
            "rede": "col_004",
            "rede_publica": "publica",
            "metricas": {
                ("ANOS_INICIAIS", "APROVACAO"): "col_006",
                ("ANOS_FINAIS", "APROVACAO"): "col_007",
                ("ANOS_INICIAIS", "REPROVACAO"): "col_024",
                ("ANOS_FINAIS", "REPROVACAO"): "col_025",
                ("ANOS_INICIAIS", "ABANDONO"): "col_042",
                ("ANOS_FINAIS", "ABANDONO"): "col_043",
            },
        }
        for ano in range(2017, 2024)
    },
}

COLUNAS_SILVER = [
    "ANO",
    "UF",
    "ETAPA",
    "REDE",
    "INDICADOR",
    "VALOR",
    "REDE_ORIGEM",
    "LOCALIZACAO_ORIGEM",
    "ARQUIVO_ORIGEM",
    "LINHA_ORIGEM_BRONZE",
    "COLUNA_ORIGEM",
]

ORDEM_ETAPA = {
    "ANOS_INICIAIS": 1,
    "ANOS_FINAIS": 2,
}

ORDEM_INDICADOR = {
    "APROVACAO": 1,
    "REPROVACAO": 2,
    "ABANDONO": 3,
}


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return texto.casefold()


def converter_uf(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto.upper() in UFS:
        return texto.upper()

    return NOMES_UF.get(
        normalizar_texto(texto)
    )


def converter_valor(valor, ano, uf, etapa, indicador):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()

    if texto in {"", "--"}:
        return pd.NA

    texto = texto.replace(",", ".")

    try:
        numero = float(texto)
    except ValueError as exc:
        raise RuntimeError(
            f"Valor não numérico inesperado: "
            f"ano={ano}, UF={uf}, etapa={etapa}, "
            f"indicador={indicador}, valor={valor!r}"
        ) from exc

    # As planilhas antigas podem expor resíduos binários como
    # 84.39999999999999. As taxas são publicadas em décimos.
    numero = round(numero, 1)

    if not 0 <= numero <= 100:
        raise RuntimeError(
            f"Taxa fora do domínio 0–100: "
            f"ano={ano}, UF={uf}, etapa={etapa}, "
            f"indicador={indicador}, valor={numero}"
        )

    return numero


def validar_colunas_bronze(df, ano, config):
    obrigatorias = {
        "_arquivo_origem",
        "_linha_origem",
        "col_001",
        config["uf"],
        config["localizacao"],
        config["rede"],
        *config["metricas"].values(),
    }

    faltantes = sorted(
        obrigatorias.difference(df.columns)
    )

    if faltantes:
        raise RuntimeError(
            f"Rendimento {ano}: colunas Bronze ausentes: "
            f"{faltantes}"
        )


def selecionar_publica_total(df, ano, config):
    ano_normalizado = df["col_001"].map(
        normalizar_texto
    )
    localizacao = df[config["localizacao"]].map(
        normalizar_texto
    )
    rede = df[config["rede"]].map(
        normalizar_texto
    )

    selecionado = df.loc[
        (ano_normalizado == str(ano))
        & (localizacao == "total")
        & (rede == config["rede_publica"])
    ].copy()

    selecionado["_UF_CANONICA"] = (
        selecionado[config["uf"]]
        .map(converter_uf)
    )

    # Remove Brasil e regiões geográficas nas edições que os incluem.
    selecionado = selecionado[
        selecionado["_UF_CANONICA"].notna()
    ].copy()

    ufs_encontradas = set(
        selecionado["_UF_CANONICA"]
    )

    faltantes = sorted(
        UFS.difference(ufs_encontradas)
    )
    extras = sorted(
        ufs_encontradas.difference(UFS)
    )

    if faltantes or extras:
        raise RuntimeError(
            f"Rendimento {ano}: conjunto de UFs inesperado.\n"
            f"Faltantes: {faltantes}\n"
            f"Extras: {extras}"
        )

    duplicadas = (
        selecionado["_UF_CANONICA"]
        .duplicated(keep=False)
    )

    if duplicadas.any():
        valores = (
            selecionado.loc[
                duplicadas,
                [
                    "_UF_CANONICA",
                    config["uf"],
                    config["localizacao"],
                    config["rede"],
                    "_linha_origem",
                ],
            ]
            .sort_values("_UF_CANONICA")
            .to_dict("records")
        )

        raise RuntimeError(
            f"Rendimento {ano}: mais de uma linha "
            f"pública-total para a mesma UF: {valores}"
        )

    if len(selecionado) != 27:
        raise RuntimeError(
            f"Rendimento {ano}: eram esperadas 27 linhas "
            f"públicas-total; encontradas {len(selecionado)}."
        )

    return selecionado


def transformar_ano(ano):
    config = CONFIG[ano]
    caminho = (
        BRONZE_DIR
        / f"rendimento_{ano}.parquet"
    )

    if not caminho.exists():
        raise FileNotFoundError(
            f"Bronze ausente: {caminho}"
        )

    df = pd.read_parquet(
        caminho
    )

    validar_colunas_bronze(
        df=df,
        ano=ano,
        config=config,
    )

    selecionado = selecionar_publica_total(
        df=df,
        ano=ano,
        config=config,
    )

    registros = []

    for _, linha in selecionado.iterrows():
        uf = linha["_UF_CANONICA"]
        rede_origem = str(
            linha[config["rede"]]
        ).strip()
        localizacao_origem = str(
            linha[config["localizacao"]]
        ).strip()
        arquivo_origem = str(
            linha["_arquivo_origem"]
        ).strip()
        linha_origem = int(
            linha["_linha_origem"]
        )

        for (
            etapa,
            indicador,
        ), coluna_origem in config[
            "metricas"
        ].items():
            valor = converter_valor(
                valor=linha[coluna_origem],
                ano=ano,
                uf=uf,
                etapa=etapa,
                indicador=indicador,
            )

            registros.append(
                {
                    "ANO": ano,
                    "UF": uf,
                    "ETAPA": etapa,
                    "REDE": "PUBLICA",
                    "INDICADOR": indicador,
                    "VALOR": valor,
                    "REDE_ORIGEM": rede_origem,
                    "LOCALIZACAO_ORIGEM": localizacao_origem,
                    "ARQUIVO_ORIGEM": arquivo_origem,
                    "LINHA_ORIGEM_BRONZE": linha_origem,
                    "COLUNA_ORIGEM": coluna_origem,
                }
            )

    resultado = pd.DataFrame(
        registros,
        columns=COLUNAS_SILVER,
    )

    esperado = 27 * 2 * 3

    if len(resultado) != esperado:
        raise RuntimeError(
            f"Rendimento {ano}: esperado {esperado} "
            f"registros Silver; obtido {len(resultado)}."
        )

    return resultado


def validar_grao(df):
    grao = [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "INDICADOR",
    ]

    duplicadas = df.duplicated(
        grao,
        keep=False,
    )

    if duplicadas.any():
        exemplo = (
            df.loc[
                duplicadas,
                grao,
            ]
            .head(20)
            .to_dict("records")
        )

        raise RuntimeError(
            "Duplicidade no grão analítico da Silver: "
            f"{exemplo}"
        )


def ordenar(df):
    trabalho = df.copy()

    trabalho["_ordem_etapa"] = (
        trabalho["ETAPA"]
        .map(ORDEM_ETAPA)
    )
    trabalho["_ordem_indicador"] = (
        trabalho["INDICADOR"]
        .map(ORDEM_INDICADOR)
    )

    trabalho = (
        trabalho.sort_values(
            [
                "ANO",
                "UF",
                "_ordem_etapa",
                "_ordem_indicador",
            ]
        )
        .drop(
            columns=[
                "_ordem_etapa",
                "_ordem_indicador",
            ]
        )
        .reset_index(drop=True)
    )

    return trabalho


def main():
    print("=" * 110)
    print(
        "CAMADA SILVER — TRANSFORMAÇÃO DO RENDIMENTO ESCOLAR"
    )
    print("=" * 110)
    print()

    if set(CONFIG) != set(ANOS):
        raise RuntimeError(
            "CONFIG não corresponde exatamente a 2007–2023."
        )

    partes = []

    for ano in ANOS:
        parte = transformar_ano(
            ano
        )
        partes.append(
            parte
        )

        nulos = int(
            parte["VALOR"].isna().sum()
        )

        print(
            f"[OK] {ano} — "
            f"{len(parte):,} registros — "
            f"27 UFs — "
            f"valores ausentes: {nulos:,}"
        )

    resultado = pd.concat(
        partes,
        ignore_index=True,
    )

    validar_grao(
        resultado
    )

    resultado["ANO"] = (
        resultado["ANO"]
        .astype("int16")
    )

    resultado["VALOR"] = pd.array(
        resultado["VALOR"],
        dtype="Float64",
    )

    resultado["LINHA_ORIGEM_BRONZE"] = (
        resultado["LINHA_ORIGEM_BRONZE"]
        .astype("int64")
    )

    resultado = ordenar(
        resultado
    )

    esperado_total = (
        len(ANOS)
        * 27
        * 2
        * 3
    )

    if len(resultado) != esperado_total:
        raise RuntimeError(
            f"Total Silver inesperado. "
            f"Esperado={esperado_total:,}; "
            f"obtido={len(resultado):,}."
        )

    SILVER_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino = (
        SILVER_DIR
        / ARQUIVO_SILVER
    )

    resultado.to_parquet(
        destino,
        index=False,
        engine="pyarrow",
        compression="snappy",
    )

    releitura = pd.read_parquet(
        destino
    )

    if len(releitura) != len(resultado):
        raise RuntimeError(
            "Quantidade de linhas mudou após releitura do Parquet."
        )

    if list(releitura.columns) != COLUNAS_SILVER:
        raise RuntimeError(
            "Esquema mudou após releitura do Parquet."
        )

    print()
    print("=" * 110)
    print("RESULTADO")
    print("=" * 110)
    print(f"Arquivo: {destino}")
    print(
        f"Linhas: {len(resultado):,}"
    )
    print(
        f"Anos: {resultado['ANO'].min()}–"
        f"{resultado['ANO'].max()}"
    )
    print(
        f"UFs: {resultado['UF'].nunique()}"
    )
    print(
        "Etapas: "
        + ", ".join(
            sorted(
                resultado["ETAPA"].unique()
            )
        )
    )
    print(
        "Indicadores: "
        + ", ".join(
            sorted(
                resultado["INDICADOR"].unique()
            )
        )
    )
    print(
        "Rede canônica: PUBLICA"
    )
    print(
        f"Valores ausentes: "
        f"{int(resultado['VALOR'].isna().sum()):,}"
    )
    print()
    print(
        "SILVER DO RENDIMENTO ESCOLAR GERADA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
