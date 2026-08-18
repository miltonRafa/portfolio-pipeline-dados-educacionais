from pathlib import Path
import unicodedata

import pandas as pd


BRONZE_DIR = Path("data/bronze/tdi")
SILVER_DIR = Path("data/silver/tdi")

ARQUIVO_SILVER = "tdi_2007_2023.parquet"

ANOS = list(range(2007, 2024))

UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
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

# Configuração explícita derivada da auditoria da Bronze.
# Não há inferência automática de colunas.
CONFIG = {
    **{
        ano: {
            "uf": "col_003",
            "localizacao": "col_004",
            "rede": "col_005",
            "rede_publica": "publico",
            "metricas": {
                "ANOS_INICIAIS": "col_015",
                "ANOS_FINAIS": "col_016",
            },
        }
        for ano in range(2007, 2011)
    },
    **{
        ano: {
            "uf": "col_003",
            "localizacao": "col_004",
            "rede": "col_005",
            "rede_publica": "publico",
            "metricas": {
                "ANOS_INICIAIS": "col_007",
                "ANOS_FINAIS": "col_008",
            },
        }
        for ano in range(2011, 2015)
    },
    2015: {
        "uf": "col_004",
        "localizacao": "col_005",
        "rede": "col_006",
        "rede_publica": "publica",
        "metricas": {
            "ANOS_INICIAIS": "col_008",
            "ANOS_FINAIS": "col_009",
        },
    },
    2016: {
        "uf": "col_003",
        "localizacao": "col_004",
        "rede": "col_005",
        "rede_publica": "publica",
        "metricas": {
            "ANOS_INICIAIS": "col_007",
            "ANOS_FINAIS": "col_008",
        },
    },
    **{
        ano: {
            "uf": "col_002",
            "localizacao": "col_003",
            "rede": "col_004",
            "rede_publica": "publica",
            "metricas": {
                "ANOS_INICIAIS": "col_006",
                "ANOS_FINAIS": "col_007",
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
    "TDI",
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


def converter_valor(valor, ano, uf, etapa):
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
            f"TDI não numérica inesperada: "
            f"ano={ano}, UF={uf}, etapa={etapa}, valor={valor!r}"
        ) from exc

    numero = round(numero, 1)

    if not 0 <= numero <= 100:
        raise RuntimeError(
            f"TDI fora do domínio 0–100: "
            f"ano={ano}, UF={uf}, etapa={etapa}, valor={numero}"
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
            f"TDI {ano}: colunas Bronze ausentes: {faltantes}"
        )


def selecionar_publica_total(df, ano, config):
    ano_normalizado = df["col_001"].map(normalizar_texto)
    localizacao = df[config["localizacao"]].map(normalizar_texto)
    rede = df[config["rede"]].map(normalizar_texto)

    selecionado = df.loc[
        (ano_normalizado == str(ano))
        & (localizacao == "total")
        & (rede == config["rede_publica"])
    ].copy()

    selecionado["_UF_CANONICA"] = (
        selecionado[config["uf"]]
        .map(converter_uf)
    )

    # Em 2017–2023, a fonte inclui Brasil e regiões na mesma coluna.
    # O mapeamento abaixo mantém somente as 27 UFs.
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
            f"TDI {ano}: conjunto de UFs inesperado.\n"
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
            f"TDI {ano}: mais de uma linha pública-total "
            f"para a mesma UF: {valores}"
        )

    if len(selecionado) != 27:
        raise RuntimeError(
            f"TDI {ano}: esperadas 27 linhas públicas-total; "
            f"encontradas {len(selecionado)}."
        )

    return selecionado


def transformar_ano(ano):
    config = CONFIG[ano]
    caminho = BRONZE_DIR / f"tdi_{ano}.parquet"

    if not caminho.exists():
        raise FileNotFoundError(
            f"Bronze ausente: {caminho}"
        )

    df = pd.read_parquet(caminho)

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
        rede_origem = str(linha[config["rede"]]).strip()
        localizacao_origem = str(
            linha[config["localizacao"]]
        ).strip()
        arquivo_origem = str(
            linha["_arquivo_origem"]
        ).strip()
        linha_origem = int(
            linha["_linha_origem"]
        )

        for etapa, coluna_origem in config["metricas"].items():
            valor = converter_valor(
                valor=linha[coluna_origem],
                ano=ano,
                uf=uf,
                etapa=etapa,
            )

            registros.append(
                {
                    "ANO": ano,
                    "UF": uf,
                    "ETAPA": etapa,
                    "REDE": "PUBLICA",
                    "TDI": valor,
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

    esperado = 27 * 2

    if len(resultado) != esperado:
        raise RuntimeError(
            f"TDI {ano}: esperado {esperado} registros Silver; "
            f"obtido {len(resultado)}."
        )

    return resultado


def validar_grao(df):
    grao = [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
    ]

    duplicadas = df.duplicated(
        grao,
        keep=False,
    )

    if duplicadas.any():
        exemplo = (
            df.loc[duplicadas, grao]
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

    trabalho = (
        trabalho.sort_values(
            [
                "ANO",
                "UF",
                "_ordem_etapa",
            ]
        )
        .drop(columns=["_ordem_etapa"])
        .reset_index(drop=True)
    )

    return trabalho


def main():
    print("=" * 110)
    print(
        "CAMADA SILVER — TRANSFORMAÇÃO DA DISTORÇÃO IDADE-SÉRIE (TDI)"
    )
    print("=" * 110)
    print()

    if set(CONFIG) != set(ANOS):
        raise RuntimeError(
            "CONFIG não corresponde exatamente a 2007–2023."
        )

    partes = []

    for ano in ANOS:
        parte = transformar_ano(ano)
        partes.append(parte)

        nulos = int(
            parte["TDI"].isna().sum()
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

    validar_grao(resultado)

    resultado["ANO"] = (
        resultado["ANO"]
        .astype("int16")
    )

    resultado["TDI"] = pd.array(
        resultado["TDI"],
        dtype="Float64",
    )

    resultado["LINHA_ORIGEM_BRONZE"] = (
        resultado["LINHA_ORIGEM_BRONZE"]
        .astype("int64")
    )

    resultado = ordenar(resultado)

    esperado_total = len(ANOS) * 27 * 2

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

    releitura = pd.read_parquet(destino)

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
    print(f"Linhas: {len(resultado):,}")
    print(
        f"Anos: {resultado['ANO'].min()}–"
        f"{resultado['ANO'].max()}"
    )
    print(f"UFs: {resultado['UF'].nunique()}")
    print(
        "Etapas: "
        + ", ".join(sorted(resultado["ETAPA"].unique()))
    )
    print("Rede canônica: PUBLICA")
    print(
        f"Valores ausentes: "
        f"{int(resultado['TDI'].isna().sum()):,}"
    )
    print()
    print(
        "SILVER DA TDI GERADA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
