from pathlib import Path
import re
import unicodedata

import pandas as pd


BRONZE_DIR = Path("data/bronze/ideb")
SILVER_DIR = Path("data/silver/ideb")

ARQUIVO_SILVER = "ideb_2007_2023.parquet"

ARQUIVOS = {
    "ANOS_INICIAIS": BRONZE_DIR / "ideb_ai.parquet",
    "ANOS_FINAIS": BRONZE_DIR / "ideb_af.parquet",
}

ANOS = [
    2007,
    2009,
    2011,
    2013,
    2015,
    2017,
    2019,
    2021,
    2023,
]

UF_MAP = {
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
    "m. g. do sul": "MS",
    "minas gerais": "MG",
    "para": "PA",
    "paraiba": "PB",
    "parana": "PR",
    "pernambuco": "PE",
    "piaui": "PI",
    "rio de janeiro": "RJ",
    "rio grande do norte": "RN",
    "r. g. do norte": "RN",
    "rio grande do sul": "RS",
    "r. g. do sul": "RS",
    "rondonia": "RO",
    "roraima": "RR",
    "santa catarina": "SC",
    "sao paulo": "SP",
    "sergipe": "SE",
    "tocantins": "TO",
}

UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}

REDE_PUBLICA_ORIGEM = "publica (4)"

COLUNAS_SILVER = [
    "ANO",
    "UF",
    "ETAPA",
    "REDE",
    "IDEB",
    "GEOGRAFIA_ORIGEM",
    "REDE_ORIGEM",
    "ARQUIVO_ORIGEM",
    "ABA_ORIGEM",
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
    texto = re.sub(r"\s+", " ", texto)

    return texto.casefold()


def converter_uf(valor):
    return UF_MAP.get(
        normalizar_texto(valor)
    )


def localizar_colunas_ideb(df, etapa):
    tecnica = df[
        df["_linha_origem"] == 10
    ]

    if len(tecnica) != 1:
        raise RuntimeError(
            f"{etapa}: esperada exatamente uma linha técnica "
            f"com _linha_origem=10; encontradas {len(tecnica)}."
        )

    linha = tecnica.iloc[0]
    mapa = {}

    for ano in ANOS:
        alvo = f"VL_OBSERVADO_{ano}"

        encontradas = [
            coluna
            for coluna in df.columns
            if (
                str(coluna).startswith("col_")
                and str(linha[coluna]).strip() == alvo
            )
        ]

        if len(encontradas) != 1:
            raise RuntimeError(
                f"{etapa}: variável técnica {alvo!r} deveria "
                f"aparecer exatamente uma vez; encontradas={encontradas}."
            )

        mapa[ano] = encontradas[0]

    return mapa


def converter_valor(valor, etapa, ano, uf):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()

    if texto in {"", "-", "--"}:
        return pd.NA

    texto = texto.replace(",", ".")

    try:
        numero = float(texto)
    except ValueError as exc:
        raise RuntimeError(
            f"IDEB não numérico inesperado: "
            f"etapa={etapa}, ano={ano}, UF={uf}, valor={valor!r}"
        ) from exc

    numero = round(numero, 1)

    if not 0 <= numero <= 10:
        raise RuntimeError(
            f"IDEB fora do domínio 0–10: "
            f"etapa={etapa}, ano={ano}, UF={uf}, valor={numero}"
        )

    return numero


def validar_colunas_bronze(df, etapa):
    obrigatorias = {
        "col_001",
        "col_002",
        "_arquivo_origem",
        "_aba_origem",
        "_linha_origem",
        "_etapa_origem",
    }

    faltantes = sorted(
        obrigatorias.difference(df.columns)
    )

    if faltantes:
        raise RuntimeError(
            f"{etapa}: colunas Bronze ausentes: {faltantes}"
        )


def selecionar_ufs_publicas(df, etapa):
    trabalho = df.copy()

    trabalho["_UF_CANONICA"] = (
        trabalho["col_001"]
        .map(converter_uf)
    )

    trabalho["_REDE_NORMALIZADA"] = (
        trabalho["col_002"]
        .map(normalizar_texto)
    )

    selecionado = trabalho[
        trabalho["_UF_CANONICA"].notna()
        & (
            trabalho["_REDE_NORMALIZADA"]
            == REDE_PUBLICA_ORIGEM
        )
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
            f"{etapa}: conjunto de UFs públicas inesperado.\n"
            f"Faltantes: {faltantes}\n"
            f"Extras: {extras}"
        )

    duplicadas = (
        selecionado["_UF_CANONICA"]
        .duplicated(keep=False)
    )

    if duplicadas.any():
        exemplo = (
            selecionado.loc[
                duplicadas,
                [
                    "_UF_CANONICA",
                    "col_001",
                    "col_002",
                    "_linha_origem",
                ],
            ]
            .sort_values("_UF_CANONICA")
            .to_dict("records")
        )

        raise RuntimeError(
            f"{etapa}: mais de uma linha pública para a mesma UF: "
            f"{exemplo}"
        )

    if len(selecionado) != 27:
        raise RuntimeError(
            f"{etapa}: esperadas 27 linhas públicas; "
            f"encontradas {len(selecionado)}."
        )

    return selecionado


def transformar_etapa(etapa, caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Bronze ausente: {caminho}"
        )

    df = pd.read_parquet(caminho)

    validar_colunas_bronze(
        df=df,
        etapa=etapa,
    )

    colunas_ideb = localizar_colunas_ideb(
        df=df,
        etapa=etapa,
    )

    selecionado = selecionar_ufs_publicas(
        df=df,
        etapa=etapa,
    )

    registros = []

    for _, linha in selecionado.iterrows():
        uf = linha["_UF_CANONICA"]

        geografia_origem = str(
            linha["col_001"]
        ).strip()

        rede_origem = str(
            linha["col_002"]
        ).strip()

        arquivo_origem = str(
            linha["_arquivo_origem"]
        ).strip()

        aba_origem = str(
            linha["_aba_origem"]
        ).strip()

        linha_origem = int(
            linha["_linha_origem"]
        )

        for ano, coluna_origem in colunas_ideb.items():
            valor = converter_valor(
                valor=linha[coluna_origem],
                etapa=etapa,
                ano=ano,
                uf=uf,
            )

            registros.append(
                {
                    "ANO": ano,
                    "UF": uf,
                    "ETAPA": etapa,
                    "REDE": "PUBLICA",
                    "IDEB": valor,
                    "GEOGRAFIA_ORIGEM": geografia_origem,
                    "REDE_ORIGEM": rede_origem,
                    "ARQUIVO_ORIGEM": arquivo_origem,
                    "ABA_ORIGEM": aba_origem,
                    "LINHA_ORIGEM_BRONZE": linha_origem,
                    "COLUNA_ORIGEM": coluna_origem,
                }
            )

    resultado = pd.DataFrame(
        registros,
        columns=COLUNAS_SILVER,
    )

    esperado = 27 * len(ANOS)

    if len(resultado) != esperado:
        raise RuntimeError(
            f"{etapa}: esperados {esperado} registros Silver; "
            f"obtidos {len(resultado)}."
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

    trabalho["_ORDEM_ETAPA"] = (
        trabalho["ETAPA"]
        .map(ORDEM_ETAPA)
    )

    return (
        trabalho.sort_values(
            [
                "ANO",
                "UF",
                "_ORDEM_ETAPA",
            ]
        )
        .drop(columns=["_ORDEM_ETAPA"])
        .reset_index(drop=True)
    )


def main():
    print("=" * 110)
    print(
        "CAMADA SILVER — TRANSFORMAÇÃO DO IDEB"
    )
    print("=" * 110)
    print()

    partes = []

    for etapa, caminho in ARQUIVOS.items():
        parte = transformar_etapa(
            etapa=etapa,
            caminho=caminho,
        )

        partes.append(parte)

        print(
            f"[OK] {etapa} — "
            f"{len(parte):,} registros — "
            f"27 UFs — "
            f"9 anos — "
            f"valores ausentes: {int(parte['IDEB'].isna().sum()):,}"
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

    resultado["IDEB"] = pd.array(
        resultado["IDEB"],
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
        * len(ARQUIVOS)
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
    print(f"Linhas: {len(resultado):,}")
    print(
        "Anos: "
        + ", ".join(
            str(ano)
            for ano in sorted(resultado["ANO"].unique())
        )
    )
    print(f"UFs: {resultado['UF'].nunique()}")
    print(
        "Etapas: "
        + ", ".join(
            sorted(resultado["ETAPA"].unique())
        )
    )
    print("Rede canônica: PUBLICA")
    print(
        f"Valores ausentes: "
        f"{int(resultado['IDEB'].isna().sum()):,}"
    )
    print()
    print(
        "SILVER DO IDEB GERADA COM SUCESSO."
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
