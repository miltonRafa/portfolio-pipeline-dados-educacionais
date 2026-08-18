from pathlib import Path
import hashlib

import pandas as pd


RAW_DIR = Path("data/raw/tdi")
BRONZE_DIR = Path("data/bronze/tdi")


ARQUIVOS_ORIGEM = {
    2007: "TDI UFS 2007.xls",
    2008: "TDI UFS 2008.xls",
    2009: "DADOS TDI UF - 2009.xls",
    2010: "DADOS TDI UF - 2010.xls",
    2011: "tdi_UFs_2011.xls",
    2012: "tdi_UFs_2012.xls",
    2013: "TDI UF - 2013.xls",
    2014: "TDI UF - 2014.xls",
    2015: "TDI_UFS_2015.xlsx",
    2016: "TDI_UFS_2016.xlsx",
    2017: "TDI_BRASIL_REGIOES_UFS_2017.xlsx",
    2018: "TDI_BRASIL_REGIOES_UFS_2018.xlsx",
    2019: "TDI_BRASIL_REGIOES_UFS_2019.xlsx",
    2020: "TDI_BRASIL_REGIOES_UFS_2020.xlsx",
    2021: "TDI_BRASIL_REGIOES_UFS_2021.xlsx",
    2022: "TDI_BRASIL_REGIOES_UFS_2022.xlsx",
    2023: "TDI_BRASIL_REGIOES_UFS_2023.xlsx",
}


COLUNAS_TECNICAS = {
    "_fonte",
    "_sha256_arquivo",
    "_arquivo_origem",
    "_aba_origem",
    "_ano_referencia",
    "_indice_cabecalho_origem",
    "_linha_origem",
}


def calcular_sha256(caminho):
    sha256 = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(
            1024 * 1024
        ):
            sha256.update(bloco)

    return sha256.hexdigest()


def registrar_erro(
    erros,
    ano,
    mensagem,
):
    erros.append(
        f"{ano}: {mensagem}"
    )


def validar_ano(
    ano,
    arquivo_origem,
    erros,
):
    origem = (
        RAW_DIR
        / arquivo_origem
    )

    parquet = (
        BRONZE_DIR
        / f"tdi_{ano}.parquet"
    )

    print()
    print(f"ANO {ano}")
    print("-" * 80)

    # --------------------------------------------------
    # ARQUIVOS
    # --------------------------------------------------

    if not origem.exists():
        registrar_erro(
            erros,
            ano,
            "arquivo RAW ausente",
        )

        print(
            "[ERRO] Arquivo RAW ausente"
        )

        return 0

    if not parquet.exists():
        registrar_erro(
            erros,
            ano,
            "arquivo Bronze ausente",
        )

        print(
            "[ERRO] Arquivo Parquet ausente"
        )

        return 0

    # --------------------------------------------------
    # LEITURA
    # --------------------------------------------------

    try:
        dados = pd.read_parquet(
            parquet,
            engine="pyarrow",
        )

    except Exception as erro:
        registrar_erro(
            erros,
            ano,
            (
                "falha ao ler Parquet: "
                f"{erro}"
            ),
        )

        print(
            "[ERRO] Falha na leitura "
            "do Parquet"
        )

        return 0

    if dados.empty:
        registrar_erro(
            erros,
            ano,
            "Parquet vazio",
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
            ano,
            (
                "colunas técnicas ausentes: "
                f"{sorted(faltantes)}"
            ),
        )

        print(
            "[ERRO] Colunas técnicas "
            "ausentes"
        )

        return len(dados)

    # --------------------------------------------------
    # FONTE
    # --------------------------------------------------

    fontes = set(
        dados["_fonte"]
        .dropna()
        .unique()
    )

    if fontes != {"TDI"}:
        registrar_erro(
            erros,
            ano,
            (
                "_fonte inválida: "
                f"{fontes}"
            ),
        )

    # --------------------------------------------------
    # ANO DE REFERÊNCIA
    # --------------------------------------------------

    anos = set(
        dados["_ano_referencia"]
        .dropna()
        .unique()
    )

    if anos != {ano}:
        registrar_erro(
            erros,
            ano,
            (
                "_ano_referencia inválido: "
                f"{anos}"
            ),
        )

    # --------------------------------------------------
    # ARQUIVO DE ORIGEM
    # --------------------------------------------------

    arquivos = set(
        dados["_arquivo_origem"]
        .dropna()
        .unique()
    )

    if arquivos != {
        arquivo_origem
    }:
        registrar_erro(
            erros,
            ano,
            (
                "_arquivo_origem "
                "divergente: "
                f"{arquivos}"
            ),
        )

    # --------------------------------------------------
    # ABA DE ORIGEM
    # --------------------------------------------------

    abas = (
        dados["_aba_origem"]
        .dropna()
        .unique()
        .tolist()
    )

    if len(abas) != 1:
        registrar_erro(
            erros,
            ano,
            (
                "quantidade inválida de "
                "abas registradas: "
                f"{abas}"
            ),
        )

    # --------------------------------------------------
    # ÍNDICE DO CABEÇALHO
    # --------------------------------------------------

    indices_cabecalho = set(
        dados[
            "_indice_cabecalho_origem"
        ]
        .dropna()
        .unique()
    )

    if indices_cabecalho != {5}:
        registrar_erro(
            erros,
            ano,
            (
                "_indice_cabecalho_origem "
                "inválido: "
                f"{indices_cabecalho}"
            ),
        )

    # --------------------------------------------------
    # SHA-256
    # --------------------------------------------------

    hash_raw = calcular_sha256(
        origem
    )

    hashes_bronze = set(
        dados["_sha256_arquivo"]
        .dropna()
        .unique()
    )

    if hashes_bronze != {
        hash_raw
    }:
        registrar_erro(
            erros,
            ano,
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
            ano,
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
            ano,
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
            ano,
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

    if not colunas_fonte:
        registrar_erro(
            erros,
            ano,
            (
                "nenhuma coluna de origem "
                "foi encontrada"
            ),
        )

    # --------------------------------------------------
    # VALIDAÇÃO DOS NOMES TÉCNICOS
    # --------------------------------------------------

    colunas_esperadas = [
        f"col_{indice:03d}"
        for indice in range(
            1,
            len(colunas_fonte) + 1,
        )
    ]

    if colunas_fonte != (
        colunas_esperadas
    ):
        registrar_erro(
            erros,
            ano,
            (
                "sequência das colunas "
                "técnicas é inválida"
            ),
        )

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    erros_ano = [
        erro
        for erro in erros
        if erro.startswith(
            f"{ano}:"
        )
    ]

    print(
        f"Linhas: {len(dados):,}"
    )

    print(
        "Colunas da fonte: "
        f"{len(colunas_fonte)}"
    )

    if len(abas) == 1:
        print(
            f"Aba: {abas[0]!r}"
        )

    print(
        "SHA-256: "
        + (
            "OK"
            if hashes_bronze
            == {hash_raw}
            else "ERRO"
        )
    )

    if not erros_ano:
        print("Status: OK")
    else:
        print("Status: ERRO")

        for erro in erros_ano:
            print(
                "     "
                + erro
            )

    return len(dados)


def main():
    print("=" * 110)
    print(
        "VALIDAÇÃO FINAL — "
        "BRONZE TDI"
    )
    print("=" * 110)

    erros = []
    total_linhas = 0

    for ano in sorted(
        ARQUIVOS_ORIGEM
    ):
        total_linhas += (
            validar_ano(
                ano=ano,
                arquivo_origem=(
                    ARQUIVOS_ORIGEM[
                        ano
                    ]
                ),
                erros=erros,
            )
        )

    # --------------------------------------------------
    # QUANTIDADE TOTAL DE PARQUETS
    # --------------------------------------------------

    parquets = sorted(
        BRONZE_DIR.glob(
            "tdi_*.parquet"
        )
    )

    if len(parquets) != len(
        ARQUIVOS_ORIGEM
    ):
        erros.append(
            "GERAL: quantidade de "
            "Parquets diferente de 17"
        )

    # --------------------------------------------------
    # TOTAL DE LINHAS
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
        f"{len(ARQUIVOS_ORIGEM)}"
    )

    print(
        "Total de linhas Bronze: "
        f"{total_linhas:,}"
    )

    if total_linhas != 8989:
        erros.append(
            "GERAL: quantidade total "
            "de linhas diferente das "
            "8.989 produzidas na "
            "ingestão auditada"
        )

    # --------------------------------------------------
    # RESULTADO FINAL
    # --------------------------------------------------

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
            "da TDI falhou."
        )

    print()
    print(
        "TODOS OS 17 ARQUIVOS "
        "FORAM VALIDADOS."
    )

    print(
        "BRONZE DA TDI: OK"
    )


if __name__ == "__main__":
    main()