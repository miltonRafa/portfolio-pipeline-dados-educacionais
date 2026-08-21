from pathlib import Path
import math
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

ANOS = {
    2007,
    2009,
    2011,
    2013,
    2015,
    2017,
    2019,
    2021,
    2023,
}

ETAPAS = {
    "ANOS_INICIAIS",
    "ANOS_FINAIS",
}

PADRAO_OBSERVADO = re.compile(r"^VL_OBSERVADO_(\d{4})$")

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

COLUNAS_ESPERADAS = [
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


def converter_valor_bronze(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto in {"", "-", "--"}:
        return None

    texto = texto.replace(",", ".")

    try:
        numero = float(texto)
    except ValueError as exc:
        raise RuntimeError(
            f"Valor Bronze não numérico inesperado: {valor!r}"
        ) from exc

    return round(numero, 1)


def localizar_linha_tecnica(df, etapa):
    if "_indice_cabecalho_origem" not in df.columns:
        raise RuntimeError(
            f"{etapa}: metadado _indice_cabecalho_origem ausente."
        )

    indices = (
        df["_indice_cabecalho_origem"]
        .dropna()
        .unique()
    )

    if len(indices) != 1:
        raise RuntimeError(
            f"{etapa}: _indice_cabecalho_origem não é único: "
            f"{indices.tolist()}"
        )

    linha_origem = int(indices[0]) + 1
    linha = df[df["_linha_origem"] == linha_origem]

    if len(linha) != 1:
        raise RuntimeError(
            f"{etapa}: linha técnica _linha_origem={linha_origem} "
            "não encontrada de forma única."
        )

    return linha.iloc[0]


def localizar_colunas_ideb(df, etapa):
    linha = localizar_linha_tecnica(df, etapa)
    mapa = {}

    for ano in sorted(ANOS):
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
                f"{etapa}: {alvo} não localizado de forma única: "
                f"{encontradas}"
            )

        mapa[ano] = encontradas[0]

    anos_disponiveis = sorted(
        int(PADRAO_OBSERVADO.fullmatch(str(linha[coluna]).strip()).group(1))
        for coluna in df.columns
        if str(coluna).startswith("col_")
        and PADRAO_OBSERVADO.fullmatch(str(linha[coluna]).strip())
    )

    if not set(ANOS).issubset(anos_disponiveis):
        raise RuntimeError(
            f"{etapa}: anos analíticos ausentes em VL_OBSERVADO_YYYY. "
            f"Disponíveis: {anos_disponiveis}"
        )

    return mapa


def validar_esquema(df):
    if list(df.columns) != COLUNAS_ESPERADAS:
        raise RuntimeError(
            "\nEsquema Silver diferente do esperado.\n"
            f"Esperado: {COLUNAS_ESPERADAS}\n"
            f"Atual:    {list(df.columns)}"
        )


def validar_dominios(df):
    if set(df["ANO"]) != ANOS:
        raise RuntimeError(
            f"Conjunto de anos inesperado: "
            f"{sorted(df['ANO'].unique())}"
        )

    if set(df["UF"]) != UFS:
        raise RuntimeError(
            "Conjunto global de UFs diferente das 27 UFs."
        )

    if set(df["ETAPA"]) != ETAPAS:
        raise RuntimeError(
            f"Etapas inesperadas: "
            f"{sorted(df['ETAPA'].unique())}"
        )

    if set(df["REDE"]) != {"PUBLICA"}:
        raise RuntimeError(
            f"Rede canônica inesperada: "
            f"{df['REDE'].unique().tolist()}"
        )

    redes_origem = {
        normalizar_texto(valor)
        for valor in df["REDE_ORIGEM"].dropna().unique()
    }

    if redes_origem != {"publica (4)"}:
        raise RuntimeError(
            f"REDE_ORIGEM inesperada: {redes_origem}"
        )

    if not pd.api.types.is_numeric_dtype(
        df["IDEB"].dtype
    ):
        raise RuntimeError(
            "IDEB não possui tipo numérico."
        )

    validos = df["IDEB"].dropna()

    fora_dominio = validos[
        (validos < 0)
        | (validos > 10)
    ]

    if not fora_dominio.empty:
        raise RuntimeError(
            "Existem valores IDEB fora do intervalo 0–10."
        )


def validar_grao_e_completude(df):
    grao = [
        "ANO",
        "UF",
        "ETAPA",
        "REDE",
    ]

    if df.duplicated(grao).any():
        raise RuntimeError(
            "Há duplicidades no grão "
            "ANO + UF + ETAPA + REDE."
        )

    esperado_total = (
        len(ANOS)
        * 27
        * len(ETAPAS)
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
        )
        for ano in ANOS
        for uf in UFS
        for etapa in ETAPAS
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

    if not (por_ano == 54).all():
        raise RuntimeError(
            f"Quantidade por ano diferente de 54:\n{por_ano}"
        )

    ufs_por_ano_etapa = (
        df.groupby(
            ["ANO", "ETAPA"]
        )["UF"]
        .nunique()
    )

    if not (ufs_por_ano_etapa == 27).all():
        raise RuntimeError(
            "Quantidade de UFs por ano/etapa diferente de 27:\n"
            f"{ufs_por_ano_etapa}"
        )


def validar_alias_geograficos(df):
    aliases = {
        "RN": "R. G. do Norte",
        "RS": "R. G. do Sul",
        "MS": "M. G. do Sul",
    }

    for uf, esperado in aliases.items():
        valores = set(
            df.loc[
                df["UF"] == uf,
                "GEOGRAFIA_ORIGEM",
            ]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        if valores != {esperado}:
            raise RuntimeError(
                f"{uf}: GEOGRAFIA_ORIGEM inesperada. "
                f"Esperado={esperado!r}; atual={valores}"
            )


def validar_rastreabilidade_contra_bronze(df):
    total_comparado = 0

    for etapa, caminho in ARQUIVOS.items():
        if not caminho.exists():
            raise FileNotFoundError(
                f"Bronze ausente: {caminho}"
            )

        bronze = pd.read_parquet(
            caminho
        )

        colunas_ideb = localizar_colunas_ideb(
            df=bronze,
            etapa=etapa,
        )

        if bronze["_linha_origem"].duplicated().any():
            raise RuntimeError(
                f"{etapa}: _linha_origem duplicada na Bronze."
            )

        por_linha = bronze.set_index(
            "_linha_origem",
            drop=False,
        )

        silver_etapa = df[
            df["ETAPA"] == etapa
        ]

        for linha in silver_etapa.itertuples(index=False):
            numero_linha = int(
                linha.LINHA_ORIGEM_BRONZE
            )

            if numero_linha not in por_linha.index:
                raise RuntimeError(
                    f"{etapa}/{linha.UF}/{linha.ANO}: "
                    f"linha Bronze {numero_linha} não encontrada."
                )

            origem = por_linha.loc[
                numero_linha
            ]

            uf_origem = converter_uf(
                origem["col_001"]
            )

            if uf_origem != linha.UF:
                raise RuntimeError(
                    f"{etapa}/{linha.UF}/{linha.ANO}: "
                    f"UF da Bronze é {uf_origem!r}."
                )

            rede = normalizar_texto(
                origem["col_002"]
            )

            if rede != "publica (4)":
                raise RuntimeError(
                    f"{etapa}/{linha.UF}/{linha.ANO}: "
                    f"linha Bronze não é 'Pública (4)'."
                )

            coluna_esperada = colunas_ideb[
                int(linha.ANO)
            ]

            if linha.COLUNA_ORIGEM != coluna_esperada:
                raise RuntimeError(
                    f"{etapa}/{linha.UF}/{linha.ANO}: "
                    f"COLUNA_ORIGEM={linha.COLUNA_ORIGEM!r}; "
                    f"esperada={coluna_esperada!r}."
                )

            esperado = converter_valor_bronze(
                origem[coluna_esperada]
            )

            atual = linha.IDEB

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
                        f"{etapa}/{linha.UF}/{linha.ANO}: "
                        f"Bronze ausente, Silver={atual}."
                    )
            else:
                if atual is None:
                    raise RuntimeError(
                        f"{etapa}/{linha.UF}/{linha.ANO}: "
                        f"Bronze={esperado}, Silver ausente."
                    )

                if not math.isclose(
                    esperado,
                    atual,
                    abs_tol=1e-9,
                ):
                    raise RuntimeError(
                        f"{etapa}/{linha.UF}/{linha.ANO}: "
                        f"Bronze={esperado}, Silver={atual}."
                    )

            if (
                str(origem["_arquivo_origem"]).strip()
                != linha.ARQUIVO_ORIGEM
            ):
                raise RuntimeError(
                    f"{etapa}/{linha.UF}/{linha.ANO}: "
                    "ARQUIVO_ORIGEM não corresponde à Bronze."
                )

            if (
                str(origem["_aba_origem"]).strip()
                != linha.ABA_ORIGEM
            ):
                raise RuntimeError(
                    f"{etapa}/{linha.UF}/{linha.ANO}: "
                    "ABA_ORIGEM não corresponde à Bronze."
                )

            total_comparado += 1

    return total_comparado


def main():
    print("=" * 110)
    print(
        "VALIDAÇÃO FINAL — SILVER IDEB"
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

    validar_esquema(df)
    validar_dominios(df)
    validar_grao_e_completude(df)
    validar_alias_geograficos(df)

    total_comparado = (
        validar_rastreabilidade_contra_bronze(df)
    )

    print(
        f"Arquivo Silver: {ARQUIVO_SILVER}"
    )
    print(
        f"Linhas: {len(df):,}"
    )
    print(
        "Anos: 9/9 "
        "(2007, 2009, 2011, 2013, 2015, "
        "2017, 2019, 2021, 2023)"
    )
    print(
        "UFs por ano/etapa: 27"
    )
    print(
        "Etapas: ANOS_INICIAIS, ANOS_FINAIS"
    )
    print(
        "Rede: PUBLICA"
    )
    print(
        "Indicador: IDEB"
    )
    print(
        "Grão analítico único: OK"
    )
    print(
        "Domínio do IDEB 0–10: OK"
    )
    print(
        "Aliases RN/RS/MS preservados na proveniência e harmonizados: OK"
    )
    print(
        "Cabeçalho visual '20215' ignorado; "
        "ano identificado por VL_OBSERVADO_2021: OK"
    )
    print(
        f"Valores ausentes: "
        f"{int(df['IDEB'].isna().sum()):,}"
    )
    print(
        f"Registros comparados diretamente com a Bronze: "
        f"{total_comparado:,}"
    )
    print(
        "Rastreabilidade linha/coluna/arquivo/aba: OK"
    )
    print()
    print(
        "SILVER DO IDEB: OK"
    )
    print("=" * 110)


if __name__ == "__main__":
    main()
