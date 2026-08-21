from pathlib import Path
import re
import unicodedata

import pandas as pd


BRONZE_DIR = Path("data/bronze/ideb")

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

UF_PARA_SIGLA = {
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


def normalizar(valor):
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


def localizar_linha_tecnica(df, etapa):
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
    tecnica = df[
        df["_linha_origem"] == linha_origem
    ]

    if len(tecnica) != 1:
        raise RuntimeError(
            f"{etapa}: esperada exatamente uma linha técnica "
            f"com _linha_origem={linha_origem}; encontradas {len(tecnica)}."
        )

    return tecnica.iloc[0]


def localizar_colunas_ideb(df, etapa):
    linha = localizar_linha_tecnica(df, etapa)
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
                f"{etapa}: variável técnica {alvo!r} "
                f"deveria aparecer uma vez; encontradas {encontradas}."
            )

        mapa[ano] = encontradas[0]

    return mapa


def converter_uf_exata(valor):
    return UF_PARA_SIGLA.get(
        normalizar(valor)
    )


def eh_rede_publica(valor):
    texto = normalizar(valor)
    return (
        texto == "publica"
        or texto.startswith("publica (")
    )


def marcador_ausencia(valor):
    if pd.isna(valor):
        return True

    return str(valor).strip() in {
        "",
        "-",
        "--",
    }


def imprimir_geografias_nao_mapeadas(df):
    valores = []

    for valor in df["col_001"].dropna():
        bruto = str(valor).strip()

        if not bruto:
            continue

        if converter_uf_exata(bruto) is not None:
            continue

        normalizado = normalizar(bruto)

        if (
            "rio grande" in normalizado
            or "mato grosso" in normalizado
            or normalizado in {"rn", "rs", "ms"}
        ):
            valores.append(bruto)

    valores = list(dict.fromkeys(valores))

    print(
        "VALORES DE GEOGRAFIA NÃO MAPEADOS RELACIONADOS A RN, RS OU MS"
    )
    print("-" * 120)

    if not valores:
        print("  Nenhum valor candidato localizado.")
    else:
        for valor in valores:
            print(
                f"  bruto={valor!r} | normalizado={normalizar(valor)!r}"
            )

    print()


def imprimir_diagnostico_linhas(
    df,
    colunas_ideb,
    ufs_faltantes,
):
    if not ufs_faltantes:
        return

    alvos = {
        sigla: nome
        for nome, sigla in UF_PARA_SIGLA.items()
        if sigla in ufs_faltantes
    }

    print(
        "DIAGNÓSTICO DAS UFs NÃO LOCALIZADAS POR CORRESPONDÊNCIA EXATA"
    )
    print("-" * 120)

    for sigla in sorted(ufs_faltantes):
        nome = alvos[sigla]
        tokens = nome.split()

        candidatos = []

        for indice, linha in df.iterrows():
            valor = linha["col_001"]
            texto = normalizar(valor)

            if not texto:
                continue

            if (
                nome in texto
                or all(token in texto for token in tokens)
            ):
                candidatos.append(
                    (indice, linha)
                )

        print(
            f"{sigla} — nome esperado normalizado: {nome!r}"
        )

        if not candidatos:
            print(
                "  Nenhuma linha cujo col_001 contenha todos os termos do nome foi localizada."
            )
            print()
            continue

        for _, linha in candidatos:
            rede = linha["col_002"]
            numero = linha["_linha_origem"]

            valores = []

            for ano, coluna in colunas_ideb.items():
                valor = linha[coluna]
                valores.append(
                    f"{ano}={valor!r}"
                )

            print(
                f"  _linha_origem={int(numero)} | "
                f"col_001={linha['col_001']!r} | "
                f"col_002={rede!r} | "
                + " | ".join(valores)
            )

        print()


def auditar_etapa(etapa, caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo Bronze ausente: {caminho}"
        )

    df = pd.read_parquet(caminho)

    colunas_ideb = localizar_colunas_ideb(
        df=df,
        etapa=etapa,
    )

    trabalho = df.copy()
    trabalho["_UF"] = trabalho[
        "col_001"
    ].map(converter_uf_exata)

    dados_uf = trabalho[
        trabalho["_UF"].notna()
    ].copy()

    publicas = dados_uf[
        dados_uf["col_002"].map(eh_rede_publica)
    ].copy()

    ufs_localizadas = set(
        dados_uf["_UF"]
    )
    ufs_esperadas = set(
        UF_PARA_SIGLA.values()
    )
    ufs_faltantes_geografia = sorted(
        ufs_esperadas - ufs_localizadas
    )

    print("=" * 120)
    print(f"IDEB — {etapa}")
    print("=" * 120)
    print(
        "Colunas IDEB observadas identificadas pela linha técnica:"
    )

    for ano, coluna in colunas_ideb.items():
        print(
            f"  {ano}: {coluna} = VL_OBSERVADO_{ano}"
        )

    print()
    print(
        f"UFs reconhecidas por correspondência exata: "
        f"{len(ufs_localizadas)}/27"
    )
    print(
        f"Linhas das UFs reconhecidas, todas as redes: "
        f"{len(dados_uf)}"
    )
    print(
        f"Linhas de rede pública nas UFs reconhecidas: "
        f"{len(publicas)}"
    )

    if ufs_faltantes_geografia:
        print(
            "UFs ainda não reconhecidas em col_001: "
            + ", ".join(ufs_faltantes_geografia)
        )
    else:
        print(
            "UFs ainda não reconhecidas em col_001: nenhuma"
        )

    print()

    contagem = (
        publicas.groupby("_UF")
        .size()
        .reindex(
            sorted(ufs_esperadas),
            fill_value=0,
        )
    )

    faltantes_publica = contagem[
        contagem == 0
    ].index.tolist()

    duplicadas = contagem[
        contagem > 1
    ].to_dict()

    if faltantes_publica:
        print(
            "UFs sem linha pública reconhecida: "
            + ", ".join(faltantes_publica)
        )
    else:
        print(
            "UFs sem linha pública reconhecida: nenhuma"
        )

    if duplicadas:
        print(
            f"UFs com mais de uma linha pública reconhecida: {duplicadas}"
        )
    else:
        print(
            "UFs com mais de uma linha pública reconhecida: nenhuma"
        )

    print()
    print("RÓTULO DE REDE PÚBLICA POR UF RECONHECIDA")
    print("-" * 120)

    exibicao = publicas[
        [
            "_UF",
            "col_001",
            "col_002",
            "_linha_origem",
        ]
    ].sort_values("_UF")

    if exibicao.empty:
        print("  Nenhuma linha pública reconhecida.")
    else:
        # iterrows é usado de propósito: nomes iniciados por "_"
        # podem ser renomeados internamente por itertuples.
        for _, linha in exibicao.iterrows():
            print(
                f"  {linha['_UF']}: "
                f"{linha['col_001']!r} | "
                f"rede={linha['col_002']!r} | "
                f"_linha_origem={int(linha['_linha_origem'])}"
            )

    print()
    print("COMPLETUDE DOS VALORES IDEB DAS LINHAS PÚBLICAS RECONHECIDAS")
    print("-" * 120)

    for ano, coluna in colunas_ideb.items():
        serie = publicas[coluna]
        ausentes = serie.map(
            marcador_ausencia
        )

        print(
            f"  {ano}: "
            f"presentes={int((~ausentes).sum())}/{len(publicas)} | "
            f"ausentes={int(ausentes.sum())}"
        )

        if ausentes.any():
            for _, linha in publicas.loc[
                ausentes,
                [
                    "_UF",
                    "col_002",
                    "_linha_origem",
                    coluna,
                ],
            ].sort_values("_UF").iterrows():
                print(
                    f"    {linha['_UF']}: "
                    f"rede={linha['col_002']!r} | "
                    f"valor={linha[coluna]!r} | "
                    f"_linha_origem={int(linha['_linha_origem'])}"
                )

    print()

    rotulos = sorted(
        {
            str(valor).strip()
            for valor in publicas["col_002"].dropna()
        }
    )

    print(
        "Rótulos públicos reconhecidos: "
        + (
            " | ".join(rotulos)
            if rotulos
            else "<nenhum>"
        )
    )
    print()

    imprimir_geografias_nao_mapeadas(
        df
    )

    imprimir_diagnostico_linhas(
        df=df,
        colunas_ideb=colunas_ideb,
        ufs_faltantes=ufs_faltantes_geografia,
    )

    if (
        len(ufs_localizadas) == 27
        and len(publicas) == 27
        and not faltantes_publica
        and not duplicadas
    ):
        print(
            "Estrutura de rede pública por UF: OK"
        )
    else:
        print(
            "Estrutura de rede pública por UF: REQUER REVISÃO"
        )

    print()


def main():
    print("=" * 120)
    print(
        "VERIFICAÇÃO FOCADA — REDE PÚBLICA E COLUNAS OBSERVADAS DO IDEB — V2"
    )
    print("=" * 120)
    print()
    print(
        "A identificação dos anos usa os nomes técnicos VL_OBSERVADO_YYYY,"
    )
    print(
        "e não o cabeçalho visual, para evitar que o erro gráfico '20215'"
    )
    print(
        "seja interpretado como ano ou altere a seleção de 2021."
    )
    print()
    print(
        "Esta versão também diagnostica UFs cuja grafia em col_001 não "
        "corresponde exatamente ao mapeamento canônico."
    )
    print()

    for etapa, caminho in ARQUIVOS.items():
        auditar_etapa(
            etapa=etapa,
            caminho=caminho,
        )

    print("=" * 120)
    print("VERIFICAÇÃO CONCLUÍDA.")
    print("Nenhum arquivo Bronze ou Silver foi alterado.")
    print("=" * 120)


if __name__ == "__main__":
    main()
