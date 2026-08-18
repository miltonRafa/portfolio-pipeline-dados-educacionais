from pathlib import Path
import hashlib

import pandas as pd


RAW_DIR = Path("data/raw/ideb")
BRONZE_DIR = Path("data/bronze/ideb")

ARQUIVO_ORIGEM = "divulgacao_regioes_ufs_ideb_2023.xlsx"

CONFIG = {
    "AI": {
        "arquivo_bronze": "ideb_ai.parquet",
        "aba": "UF e Regiões (AI)",
        "linhas": 150,
        "colunas_fonte": 120,
    },
    "AF": {
        "arquivo_bronze": "ideb_af.parquet",
        "aba": "UF e Regiões (AF)",
        "linhas": 149,
        "colunas_fonte": 110,
    },
    "EM": {
        "arquivo_bronze": "ideb_em.parquet",
        "aba": "UF e Regiões (EM)",
        "linhas": 117,
        "colunas_fonte": 110,
    },
}

COLUNAS_TECNICAS = {
    "_fonte",
    "_sha256_arquivo",
    "_arquivo_origem",
    "_aba_origem",
    "_etapa_origem",
    "_ano_referencia",
    "_indice_cabecalho_origem",
    "_linha_origem",
}


def calcular_sha256(caminho):
    sha256 = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(1024 * 1024):
            sha256.update(bloco)

    return sha256.hexdigest()


def registrar_erro(erros, etapa, mensagem):
    erros.append(
        f"{etapa}: {mensagem}"
    )


def validar_etapa(
    etapa,
    configuracao,
    hash_raw,
    erros,
):
    caminho_bronze = (
        BRONZE_DIR
        / configuracao["arquivo_bronze"]
    )

    print()
    print(f"ETAPA {etapa}")
    print("-" * 100)

    if not caminho_bronze.exists():
        registrar_erro(
            erros,
            etapa,
            "arquivo Parquet ausente",
        )

        print(
            "[ERRO] Arquivo Parquet ausente"
        )

        return

    try:
        dados = pd.read_parquet(
            caminho_bronze,
            engine="pyarrow",
        )

    except Exception as erro:
        registrar_erro(
            erros,
            etapa,
            f"falha ao ler Parquet: {erro}",
        )

        print(
            "[ERRO] Falha ao ler Parquet"
        )

        return

    # --------------------------------------------------
    # ARQUIVO NÃO VAZIO
    # --------------------------------------------------

    if dados.empty:
        registrar_erro(
            erros,
            etapa,
            "Parquet vazio",
        )

    # --------------------------------------------------
    # QUANTIDADE DE LINHAS
    # --------------------------------------------------

    linhas_esperadas = (
        configuracao["linhas"]
    )

    if len(dados) != linhas_esperadas:
        registrar_erro(
            erros,
            etapa,
            (
                "quantidade de linhas divergente: "
                f"esperado={linhas_esperadas}, "
                f"encontrado={len(dados)}"
            ),
        )

    # --------------------------------------------------
    # COLUNAS TÉCNICAS
    # --------------------------------------------------

    faltantes = (
        COLUNAS_TECNICAS
        - set(dados.columns)
    )

    if faltantes:
        registrar_erro(
            erros,
            etapa,
            (
                "colunas técnicas ausentes: "
                f"{sorted(faltantes)}"
            ),
        )

        print(
            "[ERRO] Colunas técnicas ausentes"
        )

        return

    # --------------------------------------------------
    # FONTE
    # --------------------------------------------------

    fontes = set(
        dados["_fonte"]
        .dropna()
        .unique()
    )

    if fontes != {"IDEB"}:
        registrar_erro(
            erros,
            etapa,
            f"_fonte inválida: {fontes}",
        )

    # --------------------------------------------------
    # ARQUIVO DE ORIGEM
    # --------------------------------------------------

    arquivos = set(
        dados["_arquivo_origem"]
        .dropna()
        .unique()
    )

    if arquivos != {ARQUIVO_ORIGEM}:
        registrar_erro(
            erros,
            etapa,
            (
                "_arquivo_origem divergente: "
                f"{arquivos}"
            ),
        )

    # --------------------------------------------------
    # ABA DE ORIGEM
    # --------------------------------------------------

    abas = set(
        dados["_aba_origem"]
        .dropna()
        .unique()
    )

    aba_esperada = (
        configuracao["aba"]
    )

    if abas != {aba_esperada}:
        registrar_erro(
            erros,
            etapa,
            (
                "_aba_origem divergente: "
                f"{abas}"
            ),
        )

    # --------------------------------------------------
    # ETAPA DE ORIGEM
    # --------------------------------------------------

    etapas = set(
        dados["_etapa_origem"]
        .dropna()
        .unique()
    )

    if etapas != {etapa}:
        registrar_erro(
            erros,
            etapa,
            (
                "_etapa_origem divergente: "
                f"{etapas}"
            ),
        )

    # --------------------------------------------------
    # ANO DE REFERÊNCIA DA PUBLICAÇÃO
    # --------------------------------------------------

    anos = set(
        dados["_ano_referencia"]
        .dropna()
        .unique()
    )

    if anos != {2023}:
        registrar_erro(
            erros,
            etapa,
            (
                "_ano_referencia inválido: "
                f"{anos}"
            ),
        )

    # --------------------------------------------------
    # LINHA TÉCNICA DO CABEÇALHO
    # --------------------------------------------------

    indices = set(
        dados[
            "_indice_cabecalho_origem"
        ]
        .dropna()
        .unique()
    )

    if indices != {9}:
        registrar_erro(
            erros,
            etapa,
            (
                "_indice_cabecalho_origem "
                f"inválido: {indices}"
            ),
        )

    # --------------------------------------------------
    # SHA-256
    # --------------------------------------------------

    hashes = set(
        dados["_sha256_arquivo"]
        .dropna()
        .unique()
    )

    if hashes != {hash_raw}:
        registrar_erro(
            erros,
            etapa,
            "SHA-256 divergente",
        )

    # --------------------------------------------------
    # LINHA DE ORIGEM
    # --------------------------------------------------

    if (
        dados["_linha_origem"]
        .isna()
        .any()
    ):
        registrar_erro(
            erros,
            etapa,
            (
                "_linha_origem possui "
                "valores ausentes"
            ),
        )

    if (
        dados["_linha_origem"]
        .duplicated()
        .any()
    ):
        registrar_erro(
            erros,
            etapa,
            (
                "_linha_origem possui "
                "duplicidades"
            ),
        )

    if not (
        dados["_linha_origem"]
        .is_monotonic_increasing
    ):
        registrar_erro(
            erros,
            etapa,
            (
                "_linha_origem não está "
                "em ordem crescente"
            ),
        )

    # --------------------------------------------------
    # COLUNAS DA FONTE
    # --------------------------------------------------

    colunas_fonte = [
        coluna
        for coluna in dados.columns
        if coluna.startswith("col_")
    ]

    quantidade_esperada = (
        configuracao[
            "colunas_fonte"
        ]
    )

    if (
        len(colunas_fonte)
        != quantidade_esperada
    ):
        registrar_erro(
            erros,
            etapa,
            (
                "quantidade de colunas da fonte "
                "divergente: "
                f"esperado={quantidade_esperada}, "
                f"encontrado={len(colunas_fonte)}"
            ),
        )

    colunas_esperadas = [
        f"col_{indice:03d}"
        for indice in range(
            1,
            quantidade_esperada + 1,
        )
    ]

    if colunas_fonte != colunas_esperadas:
        registrar_erro(
            erros,
            etapa,
            (
                "sequência das colunas "
                "técnicas inválida"
            ),
        )

    # --------------------------------------------------
    # MARCADORES DA LINHA TÉCNICA
    # --------------------------------------------------

    linha_tecnica = dados[
        dados["_linha_origem"] == 10
    ]

    if linha_tecnica.empty:
        registrar_erro(
            erros,
            etapa,
            (
                "linha técnica original "
                "não encontrada"
            ),
        )

    else:
        texto = " | ".join(
            linha_tecnica[
                colunas_fonte
            ]
            .iloc[0]
            .dropna()
            .astype(str)
            .tolist()
        )

        marcadores = {
            "VL_OBSERVADO_2007",
            "VL_OBSERVADO_2023",
            "VL_NOTA_MEDIA_2023",
        }

        for marcador in marcadores:
            if marcador not in texto:
                registrar_erro(
                    erros,
                    etapa,
                    (
                        "marcador técnico ausente: "
                        f"{marcador}"
                    ),
                )

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    erros_etapa = [
        erro
        for erro in erros
        if erro.startswith(
            f"{etapa}:"
        )
    ]

    print(
        f"Linhas: {len(dados):,}"
    )

    print(
        "Colunas da fonte: "
        f"{len(colunas_fonte)}"
    )

    print(
        "Aba: "
        f"{aba_esperada!r}"
    )

    print(
        "SHA-256: "
        + (
            "OK"
            if hashes == {hash_raw}
            else "ERRO"
        )
    )

    if not erros_etapa:
        print("Status: OK")

    else:
        print("Status: ERRO")

        for erro in erros_etapa:
            print(
                f"     {erro}"
            )


def main():
    print("=" * 110)
    print(
        "VALIDAÇÃO FINAL — BRONZE IDEB"
    )
    print("=" * 110)

    caminho_raw = (
        RAW_DIR / ARQUIVO_ORIGEM
    )

    if not caminho_raw.exists():
        raise FileNotFoundError(
            f"Arquivo RAW ausente: {caminho_raw}"
        )

    hash_raw = calcular_sha256(
        caminho_raw
    )

    erros = []

    for etapa, configuracao in CONFIG.items():
        validar_etapa(
            etapa=etapa,
            configuracao=configuracao,
            hash_raw=hash_raw,
            erros=erros,
        )

    # --------------------------------------------------
    # QUANTIDADE DE PARQUETS
    # --------------------------------------------------

    parquets = sorted(
        BRONZE_DIR.glob(
            "ideb_*.parquet"
        )
    )

    nomes_encontrados = {
        arquivo.name
        for arquivo in parquets
    }

    nomes_esperados = {
        configuracao[
            "arquivo_bronze"
        ]
        for configuracao
        in CONFIG.values()
    }

    if nomes_encontrados != nomes_esperados:
        erros.append(
            (
                "GERAL: conjunto de Parquets "
                "diferente do esperado. "
                f"Esperados={sorted(nomes_esperados)}; "
                f"Encontrados={sorted(nomes_encontrados)}"
            )
        )

    # --------------------------------------------------
    # RESUMO
    # --------------------------------------------------

    print()
    print("=" * 110)
    print("RESUMO")
    print("=" * 110)
    print()

    print(
        "Parquets encontrados: "
        f"{len(parquets)}"
    )

    print(
        "Parquets esperados: "
        f"{len(CONFIG)}"
    )

    print(
        f"SHA-256 RAW: {hash_raw}"
    )

    if erros:
        print()
        print(
            "ERROS ENCONTRADOS:"
        )

        for erro in erros:
            print(
                f"- {erro}"
            )

        raise RuntimeError(
            "\nValidação da Bronze "
            "do IDEB falhou."
        )

    print()
    print(
        "TODAS AS 3 ABAS "
        "FORAM VALIDADAS."
    )

    print(
        "BRONZE DO IDEB: OK"
    )


if __name__ == "__main__":
    main()