from pathlib import Path
import math
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

COLUNAS_ESPERADAS = [
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

ETAPAS = {
    "ANOS_INICIAIS",
    "ANOS_FINAIS",
}

INDICADORES = {
    "APROVACAO",
    "REPROVACAO",
    "ABANDONO",
}

# Configuração independente usada apenas para validar
# se a rastreabilidade da Silver aponta para a célula Bronze correta.
CONFIG_BRONZE = {
    2007: {
        "uf": "col_003",
        "localizacao": "col_004",
        "rede": "col_005",
        "rede_publica": "publico",
    },
    **{
        ano: {
            "uf": "col_002",
            "localizacao": "col_003",
            "rede": "col_004",
            "rede_publica": "publico",
        }
        for ano in range(2008, 2015)
    },
    2015: {
        "uf": "col_002",
        "localizacao": "col_003",
        "rede": "col_004",
        "rede_publica": "publica",
    },
    2016: {
        "uf": "col_003",
        "localizacao": "col_004",
        "rede": "col_005",
        "rede_publica": "publica",
    },
    **{
        ano: {
            "uf": "col_002",
            "localizacao": "col_003",
            "rede": "col_004",
            "rede_publica": "publica",
        }
        for ano in range(2017, 2024)
    },
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


def converter_uf_independente(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto.upper() in UFS:
        return texto.upper()

    return NOMES_UF.get(
        normalizar_texto(texto)
    )


def converter_valor_bronze_independente(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto in {"", "--"}:
        return None

    texto = texto.replace(",", ".")

    try:
        numero = float(texto)
    except ValueError as exc:
        raise RuntimeError(
            f"Valor Bronze não numérico inesperado: {valor!r}"
        ) from exc

    return round(
        numero,
        1,
    )


def validar_esquema(df):
    if list(df.columns) != COLUNAS_ESPERADAS:
        raise RuntimeError(
            "\nEsquema Silver diferente do esperado.\n"
            f"Esperado: {COLUNAS_ESPERADAS}\n"
            f"Atual:    {list(df.columns)}"
        )


def validar_dominios(df):
    if set(df["ANO"]) != set(ANOS):
        raise RuntimeError(
            "Conjunto de anos diferente de 2007–2023."
        )

    if set(df["UF"]) != UFS:
        raise RuntimeError(
            "Conjunto global de UFs diferente das 27 UFs."
        )

    if set(df["ETAPA"]) != ETAPAS:
        raise RuntimeError(
            f"Etapas inesperadas: {sorted(df['ETAPA'].unique())}"
        )

    if set(df["REDE"]) != {"PUBLICA"}:
        raise RuntimeError(
            f"Rede canônica inesperada: {df['REDE'].unique().tolist()}"
        )

    if set(df["INDICADOR"]) != INDICADORES:
        raise RuntimeError(
            "Indicadores diferentes de aprovação, "
            "reprovação e abandono."
        )

    if not pd.api.types.is_numeric_dtype(
        df["VALOR"].dtype
    ):
        raise RuntimeError(
            "VALOR não possui tipo numérico."
        )

    validos = df["VALOR"].dropna()

    fora_dominio = validos[
        (validos < 0)
        | (validos > 100)
    ]

    if not fora_dominio.empty:
        raise RuntimeError(
            "Existem taxas fora do intervalo 0–100."
        )

    if (
        df["ARQUIVO_ORIGEM"]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "ARQUIVO_ORIGEM possui ausências."
        )

    if (
        df["COLUNA_ORIGEM"]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "COLUNA_ORIGEM possui ausências."
        )

    colunas_invalidas = (
        ~df["COLUNA_ORIGEM"]
        .astype(str)
        .str.fullmatch(r"col_\d{3}")
    )

    if colunas_invalidas.any():
        raise RuntimeError(
            "COLUNA_ORIGEM contém nomes inesperados."
        )

    if (
        df["LINHA_ORIGEM_BRONZE"]
        .isna()
        .any()
    ):
        raise RuntimeError(
            "LINHA_ORIGEM_BRONZE possui ausências."
        )


def validar_grao_e_completude(df):
    grao = [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
        "INDICADOR",
    ]

    if df.duplicated(
        grao
    ).any():
        raise RuntimeError(
            "Há duplicidades no grão "
            "ANO + UF + ETAPA + REDE + INDICADOR."
        )

    esperado_total = (
        len(ANOS)
        * 27
        * 2
        * 3
    )

    if len(df) != esperado_total:
        raise RuntimeError(
            f"Total de linhas inesperado. "
            f"Esperado={esperado_total:,}; "
            f"atual={len(df):,}."
        )

    combinacoes_esperadas = {
        (
            ano,
            uf,
            etapa,
            "PUBLICA",
            indicador,
        )
        for ano in ANOS
        for uf in UFS
        for etapa in ETAPAS
        for indicador in INDICADORES
    }

    combinacoes_atuais = set(
        df[grao].itertuples(
            index=False,
            name=None,
        )
    )

    faltantes = (
        combinacoes_esperadas
        - combinacoes_atuais
    )
    extras = (
        combinacoes_atuais
        - combinacoes_esperadas
    )

    if faltantes or extras:
        raise RuntimeError(
            "\nCompletude do grão inválida.\n"
            f"Faltantes: {sorted(faltantes)[:20]}\n"
            f"Extras: {sorted(extras)[:20]}"
        )

    por_ano = (
        df.groupby("ANO")
        .size()
    )

    if not (
        por_ano == 162
    ).all():
        raise RuntimeError(
            f"Quantidade por ano diferente de 162:\n{por_ano}"
        )

    ufs_por_ano = (
        df.groupby("ANO")["UF"]
        .nunique()
    )

    if not (
        ufs_por_ano == 27
    ).all():
        raise RuntimeError(
            f"Quantidade de UFs por ano diferente de 27:\n"
            f"{ufs_por_ano}"
        )


def validar_rede_e_localizacao_origem(df):
    for ano, grupo in df.groupby(
        "ANO"
    ):
        esperado_rede = (
            CONFIG_BRONZE[int(ano)]
            ["rede_publica"]
        )

        redes = {
            normalizar_texto(valor)
            for valor in grupo[
                "REDE_ORIGEM"
            ].unique()
        }

        if redes != {esperado_rede}:
            raise RuntimeError(
                f"{ano}: REDE_ORIGEM inesperada. "
                f"Esperado={esperado_rede!r}; atual={redes}"
            )

        localizacoes = {
            normalizar_texto(valor)
            for valor in grupo[
                "LOCALIZACAO_ORIGEM"
            ].unique()
        }

        if localizacoes != {"total"}:
            raise RuntimeError(
                f"{ano}: LOCALIZACAO_ORIGEM não é Total: "
                f"{localizacoes}"
            )


def validar_rastreabilidade_contra_bronze(df):
    total_comparado = 0

    for ano in ANOS:
        config = CONFIG_BRONZE[ano]

        caminho = (
            BRONZE_DIR
            / f"rendimento_{ano}.parquet"
        )

        if not caminho.exists():
            raise FileNotFoundError(
                f"Bronze ausente: {caminho}"
            )

        bronze = pd.read_parquet(
            caminho
        )

        if bronze[
            "_linha_origem"
        ].duplicated().any():
            raise RuntimeError(
                f"{ano}: _linha_origem duplicada na Bronze."
            )

        por_linha = bronze.set_index(
            "_linha_origem",
            drop=False,
        )

        silver_ano = df[
            df["ANO"] == ano
        ]

        for linha in silver_ano.itertuples(
            index=False
        ):
            numero_linha = int(
                linha.LINHA_ORIGEM_BRONZE
            )

            if numero_linha not in por_linha.index:
                raise RuntimeError(
                    f"{ano}/{linha.UF}: linha Bronze "
                    f"{numero_linha} não encontrada."
                )

            origem = por_linha.loc[
                numero_linha
            ]

            ano_origem = normalizar_texto(
                origem["col_001"]
            )

            if ano_origem != str(ano):
                raise RuntimeError(
                    f"{ano}/{linha.UF}: ano da linha Bronze "
                    f"não corresponde ao registro Silver."
                )

            uf_origem = converter_uf_independente(
                origem[config["uf"]]
            )

            if uf_origem != linha.UF:
                raise RuntimeError(
                    f"{ano}/{linha.UF}: UF da Bronze "
                    f"é {uf_origem!r}."
                )

            localizacao = normalizar_texto(
                origem[
                    config["localizacao"]
                ]
            )

            if localizacao != "total":
                raise RuntimeError(
                    f"{ano}/{linha.UF}: linha Bronze "
                    f"não pertence à localização Total."
                )

            rede = normalizar_texto(
                origem[config["rede"]]
            )

            if rede != config[
                "rede_publica"
            ]:
                raise RuntimeError(
                    f"{ano}/{linha.UF}: linha Bronze "
                    f"não pertence ao agregado público."
                )

            if linha.COLUNA_ORIGEM not in bronze.columns:
                raise RuntimeError(
                    f"{ano}/{linha.UF}: coluna Bronze "
                    f"{linha.COLUNA_ORIGEM!r} não existe."
                )

            esperado = converter_valor_bronze_independente(
                origem[
                    linha.COLUNA_ORIGEM
                ]
            )

            atual = linha.VALOR

            if pd.isna(atual):
                atual = None
            else:
                atual = round(
                    float(atual),
                    1,
                )

            if esperado is None:
                if atual is not None:
                    raise RuntimeError(
                        f"{ano}/{linha.UF}/"
                        f"{linha.ETAPA}/"
                        f"{linha.INDICADOR}: "
                        f"Bronze é ausente, Silver={atual}."
                    )
            else:
                if atual is None:
                    raise RuntimeError(
                        f"{ano}/{linha.UF}/"
                        f"{linha.ETAPA}/"
                        f"{linha.INDICADOR}: "
                        f"Bronze={esperado}, Silver ausente."
                    )

                if not math.isclose(
                    esperado,
                    atual,
                    abs_tol=1e-9,
                ):
                    raise RuntimeError(
                        f"{ano}/{linha.UF}/"
                        f"{linha.ETAPA}/"
                        f"{linha.INDICADOR}: "
                        f"Bronze={esperado}, Silver={atual}."
                    )

            arquivo_origem = str(
                origem[
                    "_arquivo_origem"
                ]
            ).strip()

            if (
                arquivo_origem
                != linha.ARQUIVO_ORIGEM
            ):
                raise RuntimeError(
                    f"{ano}/{linha.UF}: "
                    "ARQUIVO_ORIGEM não corresponde à Bronze."
                )

            total_comparado += 1

    return total_comparado


def validar_soma_taxas(df):
    pivot = (
        df.pivot_table(
            index=[
                "ANO",
                "UF",
                "ETAPA",
                "REDE",
            ],
            columns="INDICADOR",
            values="VALOR",
            aggfunc="first",
            dropna=False,
        )
        .reset_index()
    )

    completos = pivot[
        [
            "APROVACAO",
            "REPROVACAO",
            "ABANDONO",
        ]
    ].notna().all(axis=1)

    teste = pivot.loc[
        completos
    ].copy()

    teste["SOMA"] = (
        teste["APROVACAO"]
        + teste["REPROVACAO"]
        + teste["ABANDONO"]
    )

    divergentes = teste[
        (teste["SOMA"] - 100)
        .abs()
        > 0.3
    ]

    if not divergentes.empty:
        exemplo = (
            divergentes[
                [
                    "ANO",
                    "UF",
                    "ETAPA",
                    "SOMA",
                ]
            ]
            .head(20)
            .to_dict("records")
        )

        raise RuntimeError(
            "Há combinações completas em que aprovação + "
            "reprovação + abandono difere de 100 em mais "
            f"de 0,3 ponto percentual: {exemplo}"
        )

    return len(
        teste
    )


def main():
    print("=" * 110)
    print(
        "VALIDAÇÃO FINAL — SILVER RENDIMENTO ESCOLAR"
    )
    print("=" * 110)
    print()

    caminho = (
        SILVER_DIR
        / ARQUIVO_SILVER
    )

    if not caminho.exists():
        raise FileNotFoundError(
            f"Silver ausente: {caminho}"
        )

    df = pd.read_parquet(
        caminho
    )

    validar_esquema(
        df
    )
    validar_dominios(
        df
    )
    validar_grao_e_completude(
        df
    )
    validar_rede_e_localizacao_origem(
        df
    )

    total_comparado = (
        validar_rastreabilidade_contra_bronze(
            df
        )
    )

    somas_testadas = validar_soma_taxas(
        df
    )

    print(
        f"Arquivo Silver: {ARQUIVO_SILVER}"
    )
    print(
        f"Linhas: {len(df):,}"
    )
    print(
        "Anos: 17/17 (2007–2023)"
    )
    print(
        "UFs por ano: 27"
    )
    print(
        "Etapas: ANOS_INICIAIS, ANOS_FINAIS"
    )
    print(
        "Rede: PUBLICA"
    )
    print(
        "Indicadores: APROVACAO, REPROVACAO, ABANDONO"
    )
    print(
        "Grão analítico único: OK"
    )
    print(
        "Domínio das taxas 0–100: OK"
    )
    print(
        "Marcador -- convertido apenas para ausência: OK"
    )
    print(
        f"Registros comparados diretamente com a Bronze: "
        f"{total_comparado:,}"
    )
    print(
        f"Combinações completas com soma das taxas validada: "
        f"{somas_testadas:,}"
    )
    print(
        "Rastreabilidade linha/coluna/arquivo: OK"
    )
    print()
    print(
        "SILVER DO RENDIMENTO ESCOLAR: OK"
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
