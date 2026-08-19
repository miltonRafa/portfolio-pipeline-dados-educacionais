from pathlib import Path

import pandas as pd


ARQUIVO_OFICIAL = Path(
    "data/raw/saeb/Resultados_Saeb_2023_Brasil_Estados_Municipios.xlsb"
)

BRONZE_2023 = Path(
    "data/bronze/saeb/saeb_2023.parquet"
)

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

UFS = set(UF_CODIGO_SIGLA.values())

METRICAS = {
    "AI_LP": {
        "oficial": "MEDIA_5_LP",
        "bronze_media": "col_128",
        "bronze_peso": "col_014",
    },
    "AI_MT": {
        "oficial": "MEDIA_5_MT",
        "bronze_media": "col_129",
        "bronze_peso": "col_014",
    },
    "AF_LP": {
        "oficial": "MEDIA_9_LP",
        "bronze_media": "col_130",
        "bronze_peso": "col_038",
    },
    "AF_MT": {
        "oficial": "MEDIA_9_MT",
        "bronze_media": "col_131",
        "bronze_peso": "col_038",
    },
}


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


def sigla_por_codigo(valor):
    n = numero(valor)

    if n is None:
        return None

    return UF_CODIGO_SIGLA.get(
        int(n)
    )


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

    medias_validas = medias[
        mascara
    ]

    pesos_validos = pesos[
        mascara
    ]

    if medias_validas.empty:
        return None, 0, 0.0

    valor = (
        (medias_validas * pesos_validos).sum()
        / pesos_validos.sum()
    )

    return (
        float(valor),
        int(mascara.sum()),
        float(pesos_validos.sum()),
    )


def carregar_oficial():
    if not ARQUIVO_OFICIAL.exists():
        raise FileNotFoundError(
            f"Arquivo oficial não encontrado: {ARQUIVO_OFICIAL}"
        )

    df = pd.read_excel(
        ARQUIVO_OFICIAL,
        sheet_name="Estados",
        engine="pyxlsb",
        dtype=object,
    )

    obrigatorias = {
        "ANO_SAEB",
        "CO_UF",
        "NO_UF",
        "DEPENDENCIA_ADM",
        "LOCALIZACAO",
        "CAPITAL",
        "MEDIA_5_LP",
        "MEDIA_5_MT",
        "MEDIA_9_LP",
        "MEDIA_9_MT",
    }

    faltantes = sorted(
        obrigatorias.difference(df.columns)
    )

    if faltantes:
        raise RuntimeError(
            f"Colunas oficiais ausentes: {faltantes}"
        )

    alvo = df[
        (df["ANO_SAEB"].astype(str).str.strip() == "2023")
        & (
            df["DEPENDENCIA_ADM"]
            .astype(str)
            .str.strip()
            == "Total - Federal, Estadual e Municipal"
        )
        & (
            df["LOCALIZACAO"]
            .astype(str)
            .str.strip()
            == "Total"
        )
        & (
            df["CAPITAL"]
            .astype(str)
            .str.strip()
            == "Total"
        )
    ].copy()

    alvo["UF"] = alvo[
        "CO_UF"
    ].map(sigla_por_codigo)

    ufs = set(
        alvo["UF"].dropna()
    )

    faltantes_ufs = sorted(
        UFS - ufs
    )

    extras = sorted(
        ufs - UFS
    )

    if len(alvo) != 27 or faltantes_ufs or extras:
        raise RuntimeError(
            "Estrato oficial estadual público/Total/Total inesperado.\n"
            f"Linhas={len(alvo)}\n"
            f"UFs={len(ufs)}\n"
            f"Faltantes={faltantes_ufs}\n"
            f"Extras={extras}"
        )

    if alvo["UF"].duplicated().any():
        raise RuntimeError(
            "Há mais de uma linha oficial para a mesma UF."
        )

    resultado = alvo[
        [
            "UF",
            "NO_UF",
            "MEDIA_5_LP",
            "MEDIA_5_MT",
            "MEDIA_9_LP",
            "MEDIA_9_MT",
        ]
    ].copy()

    for coluna in [
        "MEDIA_5_LP",
        "MEDIA_5_MT",
        "MEDIA_9_LP",
        "MEDIA_9_MT",
    ]:
        resultado[coluna] = resultado[
            coluna
        ].map(numero)

    return resultado.sort_values(
        "UF"
    ).reset_index(drop=True)


def carregar_bronze():
    if not BRONZE_2023.exists():
        raise FileNotFoundError(
            f"Bronze 2023 não encontrada: {BRONZE_2023}"
        )

    df = pd.read_parquet(
        BRONZE_2023
    )

    obrigatorias = {
        "_linha_origem",
        "col_003",
        "col_007",
        "col_014",
        "col_038",
        "col_128",
        "col_129",
        "col_130",
        "col_131",
    }

    faltantes = sorted(
        obrigatorias.difference(df.columns)
    )

    if faltantes:
        raise RuntimeError(
            f"Colunas Bronze ausentes: {faltantes}"
        )

    dados = df[
        df["_linha_origem"] > 1
    ].copy()

    publicas = dados[
        dados["col_007"]
        .astype(str)
        .str.strip()
        == "1"
    ].copy()

    publicas["UF"] = publicas[
        "col_003"
    ].map(sigla_por_codigo)

    ufs = set(
        publicas["UF"].dropna()
    )

    faltantes_ufs = sorted(
        UFS - ufs
    )

    if faltantes_ufs:
        raise RuntimeError(
            f"UFs ausentes na Bronze escolar: {faltantes_ufs}"
        )

    return publicas


def calcular_candidato(publicas):
    registros = []

    for uf in sorted(UFS):
        grupo = publicas[
            publicas["UF"] == uf
        ]

        registro = {
            "UF": uf,
        }

        for nome, cfg in METRICAS.items():
            valor, escolas, presentes = media_ponderada(
                grupo,
                cfg["bronze_media"],
                cfg["bronze_peso"],
            )

            registro[
                f"{nome}_CALCULADO"
            ] = valor

            registro[
                f"{nome}_ESCOLAS"
            ] = escolas

            registro[
                f"{nome}_PRESENTES"
            ] = presentes

        registros.append(
            registro
        )

    return pd.DataFrame(
        registros
    )


def comparar(oficial, candidato):
    base = oficial.merge(
        candidato,
        on="UF",
        how="outer",
        validate="one_to_one",
    )

    comparacoes = []

    for _, linha in base.iterrows():
        for nome, cfg in METRICAS.items():
            valor_oficial = numero(
                linha[cfg["oficial"]]
            )

            valor_calculado = numero(
                linha[f"{nome}_CALCULADO"]
            )

            if (
                valor_oficial is None
                or valor_calculado is None
            ):
                diferenca = None
                bate_2_decimais = False
            else:
                diferenca = (
                    valor_calculado
                    - valor_oficial
                )

                bate_2_decimais = (
                    round(valor_calculado, 2)
                    == round(valor_oficial, 2)
                )

            comparacoes.append(
                {
                    "UF": linha["UF"],
                    "METRICA": nome,
                    "OFICIAL": valor_oficial,
                    "CALCULADO": valor_calculado,
                    "DIFERENCA": diferenca,
                    "DIF_ABS": (
                        abs(diferenca)
                        if diferenca is not None
                        else None
                    ),
                    "BATE_2_DECIMAIS": bate_2_decimais,
                    "ESCOLAS": int(
                        linha[f"{nome}_ESCOLAS"]
                    ),
                    "PRESENTES": float(
                        linha[f"{nome}_PRESENTES"]
                    ),
                }
            )

    return pd.DataFrame(
        comparacoes
    )


def formatar(valor, casas=4):
    if valor is None or pd.isna(valor):
        return "NA"

    return f"{float(valor):.{casas}f}"


def main():
    print("=" * 120)
    print(
        "COMPARAÇÃO SAEB 2023 — RESULTADO OFICIAL DE UF × AGREGAÇÃO DA BRONZE ESCOLAR"
    )
    print("=" * 120)
    print()

    print(
        "Estrato oficial usado:"
    )
    print(
        "  aba = Estados"
    )
    print(
        "  DEPENDENCIA_ADM = Total - Federal, Estadual e Municipal"
    )
    print(
        "  LOCALIZACAO = Total"
    )
    print(
        "  CAPITAL = Total"
    )
    print()
    print(
        "Candidato calculado:"
    )
    print(
        "  escolas com IN_PUBLICA = 1"
    )
    print(
        "  média da proficiência escolar ponderada por NU_PRESENTES da etapa"
    )
    print()

    oficial = carregar_oficial()
    publicas = carregar_bronze()
    candidato = calcular_candidato(
        publicas
    )
    comparacao = comparar(
        oficial,
        candidato,
    )

    print("=" * 120)
    print("CARDINALIDADE")
    print("=" * 120)
    print(
        f"Linhas oficiais de UF selecionadas: {len(oficial)}"
    )
    print(
        f"Escolas públicas na Bronze: {len(publicas):,}"
    )
    print(
        f"UFs no candidato: {candidato['UF'].nunique()}"
    )
    print(
        f"Comparações: {len(comparacao)}"
    )
    print()

    total = len(
        comparacao
    )

    iguais = int(
        comparacao[
            "BATE_2_DECIMAIS"
        ].sum()
    )

    print("=" * 120)
    print("RESULTADO GLOBAL")
    print("=" * 120)
    print(
        f"Valores que coincidem após arredondamento para 2 casas: "
        f"{iguais}/{total}"
    )

    dif_validas = comparacao[
        "DIF_ABS"
    ].dropna()

    print(
        f"Diferença absoluta média: {dif_validas.mean():.6f}"
    )
    print(
        f"Diferença absoluta mediana: {dif_validas.median():.6f}"
    )
    print(
        f"Maior diferença absoluta: {dif_validas.max():.6f}"
    )
    print()

    print("=" * 120)
    print("RESULTADO POR MÉTRICA")
    print("=" * 120)

    for metrica in METRICAS:
        grupo = comparacao[
            comparacao["METRICA"] == metrica
        ]

        iguais_metrica = int(
            grupo["BATE_2_DECIMAIS"].sum()
        )

        dif = grupo[
            "DIF_ABS"
        ].dropna()

        print(
            f"{metrica}: "
            f"coincidem={iguais_metrica}/27 | "
            f"dif_média={dif.mean():.6f} | "
            f"dif_máxima={dif.max():.6f}"
        )

    print()
    print("=" * 120)
    print("MAIORES DIVERGÊNCIAS")
    print("=" * 120)

    maiores = (
        comparacao.sort_values(
            "DIF_ABS",
            ascending=False,
            na_position="last",
        )
        .head(20)
    )

    for linha in maiores.itertuples(index=False):
        print(
            f"{linha.UF} | "
            f"{linha.METRICA} | "
            f"oficial={formatar(linha.OFICIAL, 2)} | "
            f"calculado={formatar(linha.CALCULADO, 4)} | "
            f"dif={formatar(linha.DIFERENCA, 4)} | "
            f"escolas={linha.ESCOLAS} | "
            f"presentes={linha.PRESENTES:.0f}"
        )

    print()
    print("=" * 120)
    print("VEREDITO")
    print("=" * 120)

    if iguais == total:
        print(
            "A ponderação por NU_PRESENTES reproduziu os 108 valores oficiais "
            "após arredondamento para 2 casas decimais."
        )
        print(
            "Essa regra pode avançar para documentação e implementação Silver, "
            "mantendo a validação contra a fonte oficial."
        )
    else:
        print(
            "A ponderação por NU_PRESENTES NÃO reproduziu integralmente "
            "os resultados oficiais de UF."
        )
        print(
            "Portanto, ela NÃO deve ser usada como regra canônica da Silver 2023."
        )
        print(
            "A planilha oficial agregada deve ser tratada como fonte canônica "
            "para os resultados estaduais de 2023, salvo nova evidência metodológica."
        )

    print()
    print(
        "Nenhum arquivo RAW, Bronze ou Silver foi alterado."
    )
    print("=" * 120)


if __name__ == "__main__":
    main()
